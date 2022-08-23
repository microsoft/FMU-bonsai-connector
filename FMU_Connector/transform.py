from typing import Dict, Any 

class Transform():
    def __init__():
        pass
    
    def transform_state(self, state: Dict[str, Any] ) ->  Dict[str, Any]:
        return state.copy() 
    
    def transform_action(self, action: Dict[str, Any]) ->  Dict[str, Any]:
        return action.copy()