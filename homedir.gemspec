# -*- encoding: utf-8 -*-
require File.expand_path('../lib/homedir/version', __FILE__)

Gem::Specification.new do |gem|
  gem.authors               = ["Christian Holtje"]
  gem.email                 = ["docwhat@gerf.org"]
  gem.description           = %q{Your home directory package management system}
  gem.summary               = %q{Manage your home manager}
  gem.homepage              = "http://home-dir.org/"
  gem.license               = "MIT"
  gem.required_ruby_version = ">= 1.8.7"

  #gem.post_install_message  = "Type 'homedir' to get started!"

  gem.executables           = `git ls-files -- bin/*`.split("\n").map{ |f| File.basename(f) }
  gem.files                 = `git ls-files`.split("\n")
  gem.test_files            = `git ls-files -- {test,spec,features}/*`.split("\n")
  gem.name                  = "homedir"
  gem.require_paths         = ["lib"]
  gem.version               = Homedir::VERSION

  gem.add_development_dependency('rake')
  gem.add_development_dependency('rspec', ["~> 2.8"])
  gem.add_development_dependency('factory_girl', ["~> 2.5.2"])

  gem.add_development_dependency('yard')
  gem.add_development_dependency('redcarpet')

  gem.add_development_dependency('guard')
  gem.add_development_dependency('guard-rspec')
  gem.add_development_dependency('guard-bundler')
  gem.add_development_dependency('guard-yard')
  gem.add_development_dependency('rb-fsevent')
  gem.add_development_dependency('growl')
end
