import torch
import os
import pickle
import numpy as np
from TissueIdentifierModel import TissueIdentifierModel
from safetensors.torch import save_file 
from safetensors.torch import load_file

class TissueIdentifier:
    def __init__(self, model_path: str, img_processor, threshold: float = 0.95, device='cpu'):
        self.model = self.load_model(model_path)
        self.threshold = threshold
        self.device = device
        self.img_processor = img_processor
        self.model.to(self.device)

    def load_model(self, model_path):
        model = TissueIdentifierModel()
        model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
        model.eval()
        return model

    def process_and_identify(self, data_dict):  # Added 'self' and 'data_dict' as parameters
        inputs = self.img_processor(images=list(data_dict.values()), return_tensors="pt")
        x_info = {key: tensor for key, tensor in zip(data_dict.keys(), inputs['pixel_values'])}

        images_tensor = inputs['pixel_values'].to(self.device)
        with torch.no_grad():
            outputs = self.model(images_tensor).reshape(-1)
            predictions = outputs.cpu().numpy()

        updated_dict = {key: x_info[key] for key, pred in zip(x_info.keys(), predictions) if pred > self.threshold}
        return updated_dict
    
    def save_tissue_tensor(self,tissue_tiles,save_path):
        tissue_tensor = {"{}_{}".format(str(key[0]),str(key[1])): tissue_tiles[key] for key in tissue_tiles.keys()}
        print(save_path+'.safetensors')
        save_file(tissue_tensor, save_path+'.safetensors')
        
    def load_tissue_tensor(self,file_path):
        tissue_tensors = load_file(file_path)
        return tissue_tensorss

    def save_tissue_pickle(self,tissue_tiles,name,save_loc):
        print(name)
        with open(os.path.join(save_loc,name+'.pkl'),'wb') as f:
            pickle.dump(tissue_tiles,f)   
