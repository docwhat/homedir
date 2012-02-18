
module Homedir
  # When possible, all exceptions raised by Homedir classes
  # will be subclassed from {Homedir::Error}.
  class Error < StandardError
  end

  # If a dependency is missing from a {Homedir::Package package} (it isn't
  # available in a {Homedir::Catalog Catalog}) then this exception is raised.
  class MissingDependencyError < Error
  end

  # The name assigned to a {Homedir::Package package} is not legal. Check the
  # message for the list of acceptable characters in a name.
  class InvalidNameError < Error
  end
end
