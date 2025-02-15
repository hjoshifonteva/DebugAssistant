class ActionRecorder:
    def __init__(self):
        self.actions = []
        
    def record_action(self, action_type, selector, value=None):
        self.actions.append({
            "type": action_type,
            "selector": selector,
            "value": value
        })