..
    :copyright: Copyright (c) 2014 ftrack

.. _release/release_notes:

*************
Release Notes
*************

.. release:: 0.1.3

    .. change:: change

        Update default :ref:`action_discover <developing/hooks/action_discover>` and
        :ref:`action_launch <developing/hooks/action_launch>` hooks to
        support new format in ftrack 3.0.3.
        :ref:`Read more <release/migration/0_1_3/developer_notes/updated_action_hooks>`

    .. change:: new

        Support launching applications with legacy ftrack plugins enabled.

    .. change:: fixed

        Fix import error causing Nuke to not launch correctly via Connect.

.. release:: 0.1.2
    :date: 2014-12-17

    .. change::

        Release to match version for package. No changes introduced.

.. release:: 0.1.1
    :date: 2014-12-02

    .. change:: new

        Support publishing independently of applications.

    .. change:: new

        Provide default actions for discovering and launching locally installed
        applications.
