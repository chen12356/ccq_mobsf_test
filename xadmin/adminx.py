
from __future__ import absolute_import
import xadmin
from .models import UserSettings, Log
from xadmin.layout import *
# 导入views模块
from xadmin import views

from django.utils.translation import ugettext_lazy as _, ugettext


class UserSettingsAdmin(object):
    model_icon = 'fa fa-cog'
    hidden_menu = True


xadmin.site.register(UserSettings, UserSettingsAdmin)


class LogAdmin(object):

    def link(self, instance):
        if instance.content_type and instance.object_id and instance.action_flag != 'delete':
            admin_url = self.get_admin_url(
                '%s_%s_change' % (instance.content_type.app_label, instance.content_type.model),
                instance.object_id)
            return "<a href='%s'>%s</a>" % (admin_url, _('Admin Object'))
        else:
            return ''

    link.short_description = ""
    link.allow_tags = True
    link.is_column = False

    list_display = ('action_time', 'user', 'ip_addr', '__str__', 'link')
    list_filter = ['user', 'action_time']
    search_fields = ['ip_addr', 'message']
    model_icon = 'fa fa-cog'


xadmin.site.register(Log, LogAdmin)


#主题设置，注册的时候要用到专用的view注册
class BaseSetting(object):
    #主题开关
    enable_themes = True
    #自带的主题
    use_bootswatch = True


xadmin.site.register(views.BaseAdminView, BaseSetting)

#全局外观
class GlobalXadminSetting(object):
    site_title = "业务安全检测平台"
    site_footer = "中国电信"
    #折叠
    menu_style = "accordion"


xadmin.site.register(views.CommAdminView,GlobalXadminSetting)

