..
    :copyright: Copyright (c) 2014 ftrack

.. _release/release_notes:

*************
Release Notes
*************

.. release:: 0.1.24
    :date: 2016-06-07

    .. change:: fixed
        :tags: Login

        Error when starting connect with invalid ftrack server URL.

.. release:: 0.1.23
    :date: 2016-05-06

    .. change:: fixed
        :tags: Events, API

        The `ftrack.connect.publish-components` event listener does not work
        correctly when using Windows.

.. release:: 0.1.22
    :date: 2016-05-02

    .. change:: new
        :tags: Events, API

        Added new `ftrack.connect.publish-components` event listener which
        can be used to publish components from applications not supporting
        the :term:`locations <ftrack:location>` framework.

    .. change:: changed
        :tags: Login

        Login details and credentials are now stored in a json file in the
        platform specific user data folder instead of using QSettings.

    .. change:: fixed
        :tags: Login

        Unable to logout on some platforms.

.. release:: 0.1.21
    :date: 2016-03-30

    .. change:: fixed
        :tags: Events, API

        Event listeners using new API may be registered twice.

.. release:: 0.1.20
    :date: 2016-03-14

    .. change:: new
        :tags: Plugins

        Added a menu option to open the default plugin directory.

    .. change:: changed
        :tags: Login

        Improved error handling for invalid server URLs.

    .. change:: new
        :tags: Login

        Added ability to login using regular users credentials via web interface
        instead of API key. Username and API key fields are therefore hidden by
        default in the ftrack connect login screen.

    .. change:: new
        :tags: Events

        ftrack connect will now respond to the ftrack.connect.discover event
        which can be used to identify if ftrack connect is running for the
        current user.

    .. change:: new
        :tags: Location

        Paths for custom locations that are implemented in the new Python
        API, :ref:`ftrack-python-api <ftrack-python-api:introduction>`,
        are now resolved in Connect.

    .. change:: new
        :tags: Location Scenario

        Added a new hook that can be used to detect problems and present
        information to the user.

        .. seealso::

            :ref:`Verify startup hook <developing/hooks/verify_startup>`

    .. change:: new
        :tags: Location Scenario

        Added a configure storage scenario widget that will be shown on startup
        if a storage scenario has not been configured on the server.

    .. change:: changed
        :tags: Event plugins

        Event plugins are now loaded for the new Python API, 
        :ref:`ftrack-python-api <ftrack-python-api:introduction>`.
        :ref:`Read more <release/migration/0.1.20/developer_notes>`

    .. change:: fixed
        :tags: Ui

        Restore :py:class:`ftrack_connect.panelcom.PanelComInstance` communication with contextSelector,
        so changes to the environments get reflected into the widgets.

.. release:: 0.1.19
    :date: 2016-01-08

    .. change:: new
        :tags: Context Selector

        Added new
        :py:class:`ftrack_connect.ui.widget.context_selector.ContextSelector`
        widget that can be used to present and browse for a context.

    .. change:: changed

        Removed BrowseTasksSmallWidget in favor of
        :py:class:`ftrack_connect.ui.widget.context_selector.ContextSelector`.

.. release:: 0.1.18
    :date: 2015-11-10

    .. change:: new

        Added new
        :py:class:`ftrack_connect.ui.widget.html_combobox.HtmlComboBox` widget
        and :py:class:`ftrack_connect.ui.widget.html_delegate.HtmlDelegate`.

.. release:: 0.1.17
    :date: 2015-10-16

    .. change:: fixed
        :tags: Actions

        The option *launch with latest* is not respected when launching *Adobe*
        applications.

    .. change:: fixed
        :tags: Developer, Actions

        When launching actions via connect, not all action data are passed when
        firing the launch event.

.. release:: 0.1.16
    :date: 2015-10-02

    .. change:: new

        Display more detailed information about ftrack connect in About window.

        .. seealso::

            :ref:`Add custom information to About window <developing/hooks/plugin_information>`

.. release:: 0.1.15
    :date: 2015-09-22

    .. change:: changed
        :tags: Entity Browser

        Added support for new workflow object icons in entity browser.

    .. change:: fixed
        :tags: Crew

        Humanized notification dates are not always correct.

    .. change:: fixed
        :tags: Publisher

        Clean up after a failed publish fails if not permitted to delete
        version.

.. release:: 0.1.14
    :date: 2015-09-08

    .. change:: new
        :tags: Actions

        Added support for launching actions from Connect.

        .. seealso :: :ref:`using/actions`

    .. change:: new
        :tags: Crew

        Added crew widgets for chat and notifications.

    .. change:: changed
        :tags: Actions

        Applications may now include *description* and *variant*.

    .. change:: changed
        :tags: Developer

        ``thumbnail.Base`` will no longer default to ellipsis shape. Use
        ``thumbnail.EllipsisBase`` for round thumbnails.

.. release:: 0.1.13
    :date: 2015-08-31

    .. change:: changed
        :tags: Publisher

        Update entity browser to support updated naming convention.

.. release:: 0.1.12
    :date: 2015-08-24

    .. change:: new
        :tags: Publisher

        Support custom object types and icons in entity browser.

.. release:: 0.1.11
    :date: 2015-06-05

    .. change:: changed
        :tags: Publisher

        File browser now defaults to home directory.

    .. change:: fixed
        :tags: Publisher

        File browser crashes if file is removed or renamed.

    .. change:: fixed
        :tags: Publisher

        File browser not being refreshed if closed and reopened.

.. release:: 0.1.10
    :date: 2015-05-06

    .. change:: fixed
        :tags: Publisher

        Can not add files via drag and drop with non-ascii characters in the path.

.. release:: 0.1.9
    :date: 2015-03-18

    .. change:: new
        :tags: Developer

        Added base widgets and connectors to be used by application plugins.

.. release:: 0.1.8
    :date: 2015-03-02

    .. change:: fixed
        :tags: Publisher

        Publisher browser breaks when objects and files have non-ascii
        characters.

    .. change:: new
        :tags: Developer, Tutorial

        Added tutorial on how to add you own custom applications and how
        to modify the environment. :ref:`Read more <developing/tutorial/custom_applications>`

    .. change:: changed
        :tags: Publisher

        Added the possibility to specify if you like to version up an existing
        version or create a new version when publishing.
        :ref:`Read more <using/publishing/choose_or_create_asset>`

.. release:: 0.1.7
    :date: 2015-02-03

    .. change:: fixed
        :tags: Publisher

        Publisher is stuck in processing state if publish fails.

.. release:: 0.1.6
    :date: 2015-01-30

    .. change:: change
        :tags: Developer

        Moved logic for finding and starting applications supported by legacy
        plugins from the ftrack connect core to the legacy plugins repository.

    .. change:: fixed

        Unable to launch NukeX on Windows.

    .. change:: fixed

        Wrong Nuke version is launched on Windows if several are installed.

    .. change:: fixed

        Hiero and HieroPlayer are not discovered on Windows.

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
