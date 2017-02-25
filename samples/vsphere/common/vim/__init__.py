# Required to distribute different parts of this
# package as multiple distribution
try:
    import pkg_resources

    pkg_resources.declare_namespace(__name__)
except ImportError:
    from pkgutil import extend_path

    __path__ = extend_path(__path__, __name__)  # @ReservedAssignment
