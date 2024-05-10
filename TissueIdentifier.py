import torch
import torch.nn.functional as F
from TissueIdentifierModel import TissueIdentifierModel

class TissueIdentifier:
    def __init__(self, model_path: str, img_processor, threshold: float = 0.95,device='cpu'):
        self.model = self.load_model(model_path)
        self.threshold = threshold
        self.device = device
        self.img_processor = img_processor
        self.model.to(self.device)

    def load_model(self, model_path):
        model = TissueIdentifierModel()
        model.load_state_dict(torch.load(model_path))
        model.eval()
        return model
    
    def process_and_identify(data_dict):

        inputs = self.img_processor(images=list(data_dict.values()), return_tensors="pt")
        x_info = {key: tensor for key, tensor in zip(data_dict.keys(), inputs['pixel_values'])}

        images_tensor = inputs['pixel_values'].to(self.device)
        with torch.no_grad():
            outputs = self.model(images_tensor).reshape(-1)
            predictions = outputs.cpu().numpy()

        updated_dict = {key: x_info[key] for key, pred in zip(x_info.keys(), predictions) if pred > self.threshold}
        return updated_dict
