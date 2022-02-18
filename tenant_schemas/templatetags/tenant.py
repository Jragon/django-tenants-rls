from functools import lru_cache
from django.conf import settings
from django.template import Library
from django.template.defaulttags import url as default_url, URLNode
from django.utils.module_loading import import_string
from tenant_schemas.utils import get_public_schema_name, clean_tenant_url
register = Library()

@lru_cache
def get_app_label(string):
    candidate = string.split(".")[-1]
    try:
        return getattr(import_string(string), "name", candidate)  # AppConfig
    except ImportError:
        return candidate

class SchemaURLNode(URLNode):
    def __init__(self, url_node):
        super(SchemaURLNode, self).__init__(url_node.view_name, url_node.args, url_node.kwargs, url_node.asvar)

    def render(self, context):
        url = super(SchemaURLNode, self).render(context)
        return clean_tenant_url(url)


@register.tag
def url(parser, token):
    return SchemaURLNode(default_url(parser, token))


@register.simple_tag(takes_context=True)
def is_public_schema(context, app):
    return not hasattr(context.request, 'tenant') or context.request.tenant.schema_name == get_public_schema_name()


@register.simple_tag()
def is_shared_app(app):
    return app["app_label"] in [get_app_label(_app) for _app in settings.SHARED_APPS]


@register.tag
def url(parser, token):
    return SchemaURLNode(default_url(parser, token))


@register.simple_tag
def public_schema():
    return get_public_schema_name()


@register.simple_tag(takes_context=True)
def is_tenant_app(context, app):
    return app["app_label"] in [get_app_label(_app) for _app in settings.TENANT_APPS]

