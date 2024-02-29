def classFactory(iface):
    from .binary_labeling_plugin import BinaryLabelingPlugin
    return BinaryLabelingPlugin(iface)