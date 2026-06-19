def classFactory(iface):
    from .GisnetPlugin import GisnetPlugin
    return GisnetPlugin(iface)
