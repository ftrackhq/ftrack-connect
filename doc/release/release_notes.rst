..
    :copyright: Copyright (c) 2014 ftrack

.. _release/release_notes:

*************
Release Notes
*************


.. release:: next
    :date: 2015-XX-XX

    .. change:: fix

        Unable to launch NukeX on Windows.

    .. change:: fix

        The wrong Nuke version is launched on Windows if several are installed.


.. release:: 0.1.5
    :date: 2015-01-26

    .. change:: change

        Include *all* environment variables when launching applications.

.. release:: 0.1.4
    :date: 2015-01-23

    .. change:: new

        Added :ref:`About <faq/where_can_i_see_information_about_my_ftrack_connect>`
        option to menu to display eg. version, logged in user and ftrack server
        url.

    .. change:: change

        Use a managed :term:`location` when publishing from adobe extensions to
        prevent publishing temporary files.

.. release:: 0.1.3
    :date: 2015-01-14

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
