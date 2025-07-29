import omni.graph.core as og
import carb


class OgnLoggingNodeInternalState:
    """Convenience class for maintaining per-node state information"""

    def __init__(self):
        """Instantiate the per-node state information"""
        self.history = []
        self.input_count = 1


class OgnLoggingNode:
    """
    The Ogn node class that logs messages to the console.
    """
    _INPUT_COUNT = 1

    @staticmethod
    def initialize(graph_context, node):
        """
        Initialize the node
        """
        try:
            connected_function_callback = OgnLoggingNode.on_connected_callback
            disconnected_function_callback = OgnLoggingNode.on_disconnected_callback
            node.register_on_connected_callback(connected_function_callback)
            node.register_on_disconnected_callback(disconnected_function_callback)

            # Ensure the node does not have any existing input attributes
            # at initializing step.
            data_input_attributes_list = node.get_attributes()
            for attr in data_input_attributes_list:
                attribute_name = attr.get_name()
                if attribute_name.startswith("inputs:dataIn"):
                    node.remove_attribute(attribute_name)

            # Create the first input attribute
            og.Controller().create_attribute(
                node,
                attr_name="inputs:dataIn0",
                attr_type=og.Type(og.BaseDataType.UNKNOWN),
                attr_port=og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT,
                attr_extended_type=og.ExtendedAttributeType.ANY
            )
        except Exception as e:
            carb.log_error(f"Error initializing OgnLoggingNode: {e}")
            raise

    @staticmethod
    def release(node):
        """
        Release the node, by resetting the internal state,
        especially the input count.
        """
        try:
            data_input_attributes_list = node.get_attributes()
            for attr in data_input_attributes_list:
                attribute_name = attr.get_name()
                if attribute_name.startswith("inputs:dataIn"):
                    node.remove_attribute(attribute_name)
        except Exception as e:
            carb.log_error(f"Error releasing OgnLoggingNode: {e}")
            raise

    @staticmethod
    def on_connected_callback(upstream_attr, downstream_attr):
        """
        Callback when an attribute is connected.
        This function mainly control the number of inputs.
        """

        # FIXME: Problem if the downstream node is not the OgnLoggingNode
        # but it has the name of inputs:dataIn.
        if not downstream_attr.get_name().startswith("inputs:dataIn"):
            return

        # === Set basic variables ===
        node = downstream_attr.get_node()
        attributes = node.get_attributes()

        # === Resolve the type ===
        try:
            if downstream_attr.get_resolved_type().base_type == og.BaseDataType.UNKNOWN:
                upstream_resolved_type = upstream_attr.get_resolved_type()
                if upstream_resolved_type.base_type != og.BaseDataType.UNKNOWN:
                    downstream_attr.set_resolved_type(upstream_resolved_type)

        except Exception as e:
            carb.log_error(f"Error in on_connected_callback: {e}")
            raise

        # === Create a new input attribute for extra data input ===
        try:
            # For readability, do not split the name by "dataIn" directly
            # current_index = int(downstream_attr.get_name()[13:])
            attribute_name = downstream_attr.get_name()
            current_index = int(attribute_name.replace("inputs:dataIn", ""))

            if current_index != OgnLoggingNode._INPUT_COUNT-1:
                return

            og.Controller().create_attribute(
                node,
                attr_name=f"inputs:dataIn{OgnLoggingNode._INPUT_COUNT}",
                attr_type=og.Type(og.BaseDataType.UNKNOWN),
                attr_port=og.AttributePortType.ATTRIBUTE_PORT_TYPE_INPUT,
                attr_extended_type=og.ExtendedAttributeType.ANY
            )
            OgnLoggingNode._INPUT_COUNT += 1

        except Exception as e:
            carb.log_error(f"Error in on_connected_callback: {e}")
            raise

    @staticmethod
    def on_disconnected_callback(upstream_attr, downstream_attr):
        """
        Callback when an attribute is disconnected.
        This function mainly control the number of inputs.
        """
        try:
            if not downstream_attr.get_name().startswith("inputs:dataIn"):
                return

            node = downstream_attr.get_node()
            attributes = node.get_attributes()

            attribute_name = downstream_attr.get_name()
            current_index = int(attribute_name.replace("inputs:dataIn", ""))

            if current_index == 0:
                return

            if current_index == OgnLoggingNode._INPUT_COUNT - 1:
                OgnLoggingNode._INPUT_COUNT -= 1
                node.remove_attribute(f"inputs:dataIn{current_index+1}")
        except Exception as e:
            carb.log_error(f"Error in on_disconnected_callback: {e}")
            raise

    @staticmethod
    def on_value_changed_callback(attr) -> None:
        pass

    @staticmethod
    def internal_state():
        """Returns an object that contains per-node state information"""
        return OgnLoggingNodeInternalState()

    @staticmethod
    def compute(db) -> bool:
        state = db.per_instance_state

        exec_in = db.inputs.execIn


        node = db.abi_node
        context = db.abi_context

        if exec_in == og.ExecutionAttributeState.DISABLED:
            return False
