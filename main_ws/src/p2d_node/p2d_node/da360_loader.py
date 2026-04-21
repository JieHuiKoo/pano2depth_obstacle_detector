import torch
from .da360 import networks

class DA360Loader:
    def __init__(self, model_path, device):
        self.device = device

        # Load checkpoint
        model_dict = torch.load(model_path, map_location=device)

        # Fill missing metadata
        model_dict.setdefault('net', 'DA360')
        model_dict.setdefault('dinov2_encoder', 'vits')
        model_dict.setdefault('height', 518)
        model_dict.setdefault('width', 1036)

        # Build model
        Net = getattr(networks, model_dict['net'])
        self.model = Net(
            model_dict['height'],
            model_dict['width'],
            dinov2_encoder=model_dict['dinov2_encoder']
        )

        # Load weights
        model_state_dict = self.model.state_dict()
        self.model.load_state_dict(
            {k: v for k, v in model_dict.items() if k in model_state_dict},
            strict=False
        )

        self.model.to(device)
        self.model.eval()

        self.height = model_dict['height']
        self.width = model_dict['width']

    def infer(self, equi_tensor):
        with torch.no_grad():
            outputs = self.model(equi_tensor)
        return outputs["pred_disp"]
