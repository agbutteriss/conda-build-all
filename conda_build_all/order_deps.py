import os


def resolve_dependencies(package_dependencies, existing_packages=None):
    """
    Given a dictionary mapping a package to its dependencies and a set of
    pre-existing packages, return a generator of packages to install, sorted by
    the required install order.

    Parameters
    ----------
    package_dependencies:
        A dict where the keys are package names, and the values lists of the
        names of their dependencies
    existing_packages:
        A set of packages that are already installed


    >>> deps = resolve_dependencies({'a': ['b', 'c'], 'b': ['c'],
                                     'c': ['d'], 'd': []})
    >>> list(deps)
    ['d', 'c', 'b', 'a']
    """

    remaining_dependencies = package_dependencies.copy()

    # Make a set to note which packages have been fully checked
    # Sets chosen as this will be checked frequently, and order doesn't matter
    complete_packages = set()

    # Create a holding list for existing packages we want to update
    hold = []

    # Ensures existing_packages is defined

    if existing_packages is None:
        existing_packages = set()

    # As long as there are packages we want to update
    while remaining_dependencies:
        # Get the 'first' element (or some arbritary one)
        start = remaining_dependencies.items()[0]

        # Create a 'frontier' stack for dependency traversing purposes
        frontier = [start[0]]
        frontier.extend(start[1])

        upstream_dependants = [start[0]]

        # While there's still dependencies to check for the 'start' package
        while frontier:
            # Always check the latest item in the path
            # Choice of this being to allow for actually ordering packages
            current_package = frontier[-1]

            # Checks if the package is already installed
            if current_package in existing_packages:
                # Checks if we want to update it
                if current_package in remaining_dependencies:
                    # If we do, holds it until the end
                    # (as we can theoretically use the current version for now)
                    hold.append(current_package)
                    remaining_dependencies.pop(current_package)

                # Once we've done this once, we don't want to do it again
                complete_packages.add(current_package)
                existing_packages.remove(current_package)

            # We either don't want to update this one, or already will have
            if current_package in complete_packages:
                frontier.pop()
                continue
            
            try:
                dependencies = remaining_dependencies[current_package]

            except KeyError:
                msg = ('The package {} is a dependency for one or more '
                       'libraries, but is not already installed, and is not '
                       'currently listed to be from package_dependencies. '
                       'Full dependency chain: {}'.format(current_package,
                                                          upstream_dependants))
                raise ValueError(msg)

            # Creating a copy of dependencies to avoid indexing issues later
            checked_deps = list(dependencies)

            # We also want to make sure a package doesn't depend on itself
            upstream_dependants.append(current_package)

            for dependency in dependencies:
                # We don't want to be doing the same package several times
                if dependency in complete_packages:
                    checked_deps.remove(dependency)
                    continue

                # We might want to update existing packages though
                # This also allows for the resolving of circular dependencies
                elif dependency in existing_packages:
                    continue

                elif dependency in upstream_dependants:
                    msg = ('Circular dependency. {}  depends on {} which '
                           'in turn depends on {}. Full chain: {}'
                           ''.format(current_package, dependency,
                                     current_package, upstream_dependants))
                    raise ValueError(msg)

            # We want to do dependencies first, for obvious reasons
            if checked_deps:
                frontier.extend(checked_deps)
                continue

            else:
                # Add the package to the set of completed packages
                complete_packages.add(current_package)

                # Remove it from the list of 'packages to be updated'
                remaining_dependencies.pop(current_package)

                # Avoid infinite loops
                # (remember that upstream_dependants[-1] == current_package)
                # (and frontier[-1] == current_package)
                upstream_dependants.pop()
                frontier.pop()

                yield current_package

    # Makes the order in which 'hold' packages are updated consistent
    # (alphabetical order)
    hold.sort()

    # Yields the packages that have been held back
    for p in hold:
        yield p
