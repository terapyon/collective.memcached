from plone.app.registry.browser import controlpanel
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from plone.registry.interfaces import IRecordModifiedEvent
from collective.memcached.interfaces import IMemcachedControlPanel
from collective.memcached.interfaces import IMemcachedClient
from plone.memoize.interfaces import ICacheChooser
from collective.memcached import _


class MemcachedControlPanelForm(controlpanel.RegistryEditForm):
    schema = IMemcachedControlPanel
    id = "memcached-settings"
    label = _(u"Memcached utility settings")
    description = _(u"Set memcached servers and ports with below form.")

    def updateFields(self):
        super(MemcachedControlPanelForm, self).updateFields()

    def updateWidgets(self):
        super(MemcachedControlPanelForm, self).updateWidgets()


class MemcachedControlPanel(controlpanel.ControlPanelFormWrapper):
    form = MemcachedControlPanelForm


def connection_setting_update(settings, event):
    if IRecordModifiedEvent.providedBy(event):
        # Memcached control panel setting changed
        if event.record.fieldName == 'memcached_hosts':
            mc_client = getUtility(ICacheChooser)
            mc_client.connection_setting_number += 1
