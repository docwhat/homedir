require 'homedir/hacks'
require 'fileutils'
require 'tmpdir'
require 'factory_girl'
require 'factories'

# Load all spec files
Dir["./spec/support/**/*.rb"].each {|f| require f}

RSpec.configure do |config|
  # Allows using build(), create(), etc. without the "FactoryGirl." part.
  config.include FactoryGirl::Syntax::Methods

  config.before(:each) do
    @directory = Dir.mktmpdir('homedir-spec-')
    @orig_directory = Dir.pwd
    Dir.chdir(@directory)
  end

  config.after(:each) do
    Dir.chdir(@orig_directory)
    FileUtils.rmtree(@directory)
  end
end

EXAMPLES_DIR = Pathname.new(__FILE__).dirname + 'examples'
