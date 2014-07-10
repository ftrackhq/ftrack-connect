# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import collections

from docutils import nodes
from docutils.parsers.rst import directives

from sphinx.util.compat import Directive
from sphinx import addnodes


class placeholder(nodes.comment):
    '''Placeholder node for domain summary.

    Act as a marker for where to add domain summary listing. Required as
    domain summary listing is built after doctree is resolved because it
    depends on contents of doctree (domain roles).

    '''


class AutoDomainSummaryDirective(Directive):
    '''Directive for adding an automatically generated domain summary.

    A domain summary lists each class, function and exception definition found
    in the current doctree with a link to that definition.

    The following options can be used:

        * include-methods - Also list methods for each class.

    '''

    option_spec = {
        'include-methods': directives.flag
    }

    def run(self):
        '''Process directive.

        Return placeholder node with any configured options stored on the node.

        '''
        node = placeholder()
        node['include-methods'] = 'include-methods' in self.options
        return [node]


def resolvePlaceholder(app, doctree, fromdocname):
    '''Resolve placeholder nodes into domain summary listing.

    The generated container is given a css class of 'domain-summary' to allow
    customisation of layout and display.

    '''
    items = collectDomainItems(doctree)

    container = nodes.container(classes=['domain-summary'])

    for node in doctree.traverse(placeholder):
        listing = generateDomainSummary(
            items,
            order=app.config.autodoc_member_order,
            includeMethods=node['include-methods']
        )

        for entry in listing:
            container.append(entry)

        node.replace_self(container)


def isDomainDescriptor(node):
    '''Return whether *node* is a domain object descriptor.'''
    if isinstance(node, addnodes.desc):
        objectType = node.attributes.get('desctype', None)
        if objectType in ('class', 'exception', 'function', 'method'):
            return True

    return False


def collectDomainItems(doctree):
    '''Return list of domain items from *doctree* in order encountered.'''
    items = []

    for node in doctree.traverse(condition=isDomainDescriptor):
        objectType = node.attributes.get('desctype', None)

        signature = node.children[
            node.first_child_matching_class(addnodes.desc_signature)
        ]

        name = signature.attributes.get('names')[0]
        id = signature.attributes.get('ids')[0]

        items.append((objectType, name, id))

    return items


def generateDomainSummary(items, order='alphabetic', includeMethods=True):
    '''Return domain summary for *items*.

    Each item in *items* should be in the form (objectType, name, id) and will
    be used to generate a link reference in the summary. Each object type is
    placed in a corresponding group.

    The summary entries will be ordered by *order* which can be either
    'alphabetic' or 'bysource'.

    If *includeMethods' is True then each method for a class will be added to
    the summary under the class entry.

    Example output::

        Classes
            * ClassA
                * member_1
                * member_2
            * ClassB
                * member_1
                * member_2

        Functions
            * FunctionA
            * FunctionB

        Exceptions
            * ExceptionA
            * ExceptionB

    '''
    # Group by type.
    groups = collections.OrderedDict()
    groups['class'] = {
        'title': 'Classes',
        'items': collections.OrderedDict()
    }
    groups['function'] = {
        'title': 'Functions',
        'items': collections.OrderedDict()
    }
    groups['exception'] = {
        'title': 'Exceptions',
        'items': collections.OrderedDict()
    }

    for objectType, name, id in items:

        if objectType in ('class', 'function', 'exception'):
            collection = groups[objectType]['items']
            collection[name] = {'name': name, 'id': id}

            if objectType != 'function':
                collection[name]['methods'] = {}

        elif objectType == 'method':
            # Collect under relevant parent class.
            className, methodName = name.rsplit('.', 1)
            parent = None

            if className in groups['class']['items']:
                parent = groups['class']['items'][className]

            elif className in groups['exception']['items']:
                parent = groups['exception']['items'][className]

            if parent:
                parent['methods'][methodName] = {'name': methodName, 'id': id}

    # Generate listing.
    contents = []

    orderer = sorted
    if order == 'bysource':
        orderer = lambda items: items

    for collection in groups.values():
        container = nodes.container()
        container.append(nodes.emphasis(text=collection['title']))

        listing = _generateListing(
            collection['items'],
            orderer,
            includeMethods=includeMethods
        )

        container.append(listing)
        contents.append(container)

    return contents


def _generateListing(collection, orderer, includeMethods=True):
    '''Return listing for *collection* items ordered by *orderer*.

    If *includeMethods* is True will also include a sub-listing of methods for
    classes.

    '''
    bulletList = nodes.bullet_list()
    for name, data in orderer(collection.items()):
        listItem = nodes.list_item()

        para = nodes.paragraph()

        reference = nodes.reference(
            refid=data['id'],
            reftitle=data['name']
        )

        displayName = data['name'].split('.')[-1]
        reference += nodes.Text(displayName)
        para += reference
        listItem += para

        if includeMethods and len(data.get('methods', [])):
            childBulletList = _generateListing(
                data['methods'],
                orderer,
                includeMethods=includeMethods
            )
            listItem.append(childBulletList)

        bulletList += listItem

    return bulletList


def setup(app):
    '''Register extension with Sphinx.'''
    app.add_node(placeholder)
    app.add_directive('auto-domain-summary', AutoDomainSummaryDirective)
    app.connect('doctree-resolved', resolvePlaceholder)
