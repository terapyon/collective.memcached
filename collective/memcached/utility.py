try:
    import pylibmc as memcache
except ImportError:
    import memcache

import logging

from threading import local
from zope.component import getUtility, queryUtility
from zope.interface import implements
from zope.ramcache.interfaces.ram import IRAMCache
from zope.component.interfaces import ComponentLookupError
from zope.component import adapts
from plone.registry.interfaces import IRegistry
from plone.memoize.interfaces import ICacheChooser
from plone.memoize import ram
from collective.memcached.interfaces import IMemcachedControlPanel


logger = logging.getLogger("Plone")

class MemcachedClient(object):
    """Memcached client."""

    _v_thread_local = local()

    def __call__(self):
        """Return memcached client"""
        return self.getClient()

    def getClient(self):
        """Return thread local connection to memcached."""
        connection = getattr(self._v_thread_local, 'connection', None)

        if connection is None:
            settings = self.getSettings()
            logger.info("Creating new memcache connection")
            connection = memcache.Client(settings.memcached_hosts)
            self._v_thread_local.connection = connection

        return connection

    def getSettings(self):
        registry = getUtility(IRegistry)
        return registry.forInterface(IMemcachedControlPanel)


class MemcachedCacheChooser(object):
    """"""
    implements(ICacheChooser)
    _v_thread_local = local()
    connection_setting_number = 0

    def __call__(self, fun_name):
        """
        Create new adapter for plone.memoize.ram.
        """
        client = self.getClient()
        if client is not None:
            return ram.MemcacheAdapter(client=client, globalkey=fun_name)
        else:
            return ram.RAMCacheAdapter(queryUtility(IRAMCache),
                                            globalkey=fun_name)

    def getClient(self):
        """Return thread local connection to memcached.
        """
        connection_number = getattr(self._v_thread_local, 'connection_number', 0)
        connection = getattr(self._v_thread_local, 'connection', None)
        if connection_number < self.connection_setting_number and \
                        connection is not None:
            connection = None

        if connection is None:
            try:
                registry = getUtility(IRegistry)
            except ComponentLookupError:
                logger.info("Can't have IRegistry")
                return None
            try:
                settings = registry.forInterface(IMemcachedControlPanel)
                connection = memcache.Client(settings.memcached_hosts)
            except (KeyError, TypeError):
                logger.info("Can't create memcache connection")
            else:
                logger.info("Creating new memcache connection")
                self._v_thread_local.connection = connection
                self._v_thread_local.connection_number = self.connection_setting_number

        return connection

