# coding: utf-8

from __future__ import absolute_import, division, unicode_literals

from datetime import timedelta

import six


if not hasattr(timedelta, 'total_seconds'):
    def total_seconds(delta):
        """
        Return the total number of seconds represented by this timedelta.
        Python 2.6 does not define this method.
        """
        return (delta.microseconds + (delta.seconds + delta.days * 24 * 3600) * 10 ** 6) / 10 ** 6
else:
    def total_seconds(delta):
        return delta.total_seconds()


def with_metaclass(meta, *bases, **with_metaclass_kwargs):
    """Extends the behavior of six.with_metaclass.

    The normal usage (expanded to include temporaries, to make the illustration
    easier) is:

    .. code-block:: python

        temporary_class = six.with_metaclass(meta, *bases)
        temporary_metaclass = type(temporary_class)

        class Subclass(temporary_class):
            ...

        SubclassMeta = type(Subclass)

    In this example:

    - ``temporary_class`` is a class with ``(object,)`` as its bases.
    - ``temporary_metaclass`` is a metaclass with ``(meta,)`` as its bases.
    - ``Subclass`` is a class with ``bases`` as its bases.
    - ``SubclassMeta`` is ``meta``.

    ``six.with_metaclass()`` is defined in such a way that it can make sure
    that ``Subclass`` has the correct metaclass and bases, while only using
    syntax which is common to both Python 2 and Python 3.
    ``temporary_metaclass()`` returns an instance of ``meta``, rather than an
    instance of itself / a subclass of ``temporary_class``, which is how
    ``SubclassMeta`` ends up being ``meta``, and how the temporaries don't
    appear anywhere in the final subclass.

    There are two problems with the current (as of six==1.10.0) implementation
    of ``six.with_metaclass()``, which this function solves.

    ``six.with_metaclass()`` does not define ``__prepare__()`` on the temporary
    metaclass. This means that ``meta.__prepare__()`` gets called directly,
    with bases set to ``(object,)``. If it needed to actually receive
    ``bases``, then errors might occur. For example, this was a problem when
    used with ``enum.EnumMeta`` in Python 3.6. Here we make sure that
    ``__prepare__()`` is defined on the temporary metaclass, and pass ``bases``
    to ``meta.__prepare__()``.

    Since ``temporary_class`` doesn't have the correct bases, in theory this
    could cause other problems, besides the previous one, in certain edge
    cases. To make sure that doesn't become a problem, we make sure that
    ``temporary_class`` has ``bases`` as its bases, just like the final class.
    """
    temporary_class = six.with_metaclass(meta, *bases, **with_metaclass_kwargs)
    temporary_metaclass = type(temporary_class)

    class TemporaryMetaSubclass(temporary_metaclass):
        @classmethod
        def __prepare__(cls, name, this_bases, **kwds):  # pylint:disable=unused-argument
            return meta.__prepare__(name, bases, **kwds)

    return type.__new__(TemporaryMetaSubclass, str('temporary_class'), bases, {})
