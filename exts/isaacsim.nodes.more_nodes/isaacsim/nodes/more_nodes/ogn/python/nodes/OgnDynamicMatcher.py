"""
OmniGraph core Python API:
  https://docs.omniverse.nvidia.com/kit/docs/omni.graph/latest/Overview.html

OmniGraph attribute data types:
  https://docs.omniverse.nvidia.com/kit/docs/omni.graph.docs/latest/dev/ogn/attribute_types.html

Collection of OmniGraph code examples in Python:
  https://docs.omniverse.nvidia.com/kit/docs/omni.graph.docs/latest/dev/ogn/ogn_code_samples_python.html

Collection of OmniGraph tutorials:
  https://docs.omniverse.nvidia.com/kit/docs/omni.graph.tutorials/latest/Overview.html
"""

import omni.graph.core as og
import carb


class OgnDynamicMatcherInternalState:
    """Convenience class for maintaining per-node state information"""

    def __init__(self):
        """Instantiate the per-node state information"""
        status = False


class OgnDynamicMatcher:
    """
    Node that processes dynamic inputs and passes data to outputs
    """

    @staticmethod
    def compute(db) -> bool:
        """
        Main computation function that processes dynamic inputs
        """
        try:
            # Process dynamic inputs using the pattern dataX
            processed_count = 0
            
            # Loop through potential dynamic inputs with pattern inputs:dataX
            for i in range(100):  # Support up to 100 dynamic inputs
                input_name = f"data{i}"
                
                # Check if this dynamic input exists
                if hasattr(db.inputs, input_name):
                    try:
                        # Get the input value
                        input_value = getattr(db.inputs, input_name)
                        
                        # Check if corresponding output exists
                        output_name = f"data{i}"
                        if hasattr(db.outputs, output_name):
                            # Copy input to output
                            setattr(db.outputs, output_name, input_value)
                            processed_count += 1
                            
                    except Exception as e:
                        carb.log_warn(f"Failed to process data{i}: {e}")
                        continue
                else:
                    # If we hit a gap in numbering, we can stop
                    if processed_count == 0 and i > 10:  # Allow some gaps early on
                        break
            
            # Access dynamic attributes directly from the database
            try:
                dynamic_inputs = db.getDynamicInputs()
                dynamic_outputs = db.getDynamicOutputs()
                
                # Process each dynamic input
                for input_attr in dynamic_inputs:
                    input_name = input_attr().name().getText()
                    
                    # Skip if not following our pattern
                    if not input_name.startswith("inputs:data"):
                        continue
                    
                    # Extract the suffix (e.g., "0" from "inputs:data0")
                    suffix = input_name[12:]  # Remove "inputs:data"
                    output_name = f"outputs:data{suffix}"
                    
                    # Find corresponding output
                    for output_attr in dynamic_outputs:
                        if output_attr().name().getText() == output_name:
                            try:
                                # Get input data and copy to output
                                input_data = input_attr.get()
                                output_attr.set(input_data)
                                processed_count += 1
                            except Exception as e:
                                carb.log_warn(f"Failed to copy {input_name} to {output_name}: {e}")
                            break
                            
            except Exception as e:
                carb.log_info(f"Dynamic attribute processing not available: {e}")
            
            # Trigger execution output
            db.outputs.execOut = og.ExecutionAttributeState.ENABLED
            
            if processed_count > 0:
                carb.log_info(f"DynamicMatcher processed {processed_count} input/output pairs")
            
            return True
            
        except Exception as e:
            carb.log_error(f"Error in DynamicMatcher compute: {e}")
            return False

    @staticmethod
    def initialize(graph_context, node):
        """
        Initialize the node
        """
        carb.log_info("DynamicMatcher node initialized")
        pass

