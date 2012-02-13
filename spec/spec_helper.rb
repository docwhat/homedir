require 'fakefs'
require 'fakefs/spec_helpers'
require 'factory_girl'
require 'factories'

RSpec.configure do |config|
  # Allows using build(), create(), etc. without the "FactoryGirl." part.
  config.include FactoryGirl::Syntax::Methods

  # resets the fake filesystem after each example
  config.include FakeFS::SpecHelpers
end
