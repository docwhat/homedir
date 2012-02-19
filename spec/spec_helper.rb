require 'tmpdir'
require 'factory_girl'
require 'factories'

def within_a_tmpdir
  Dir.mktmpdir('homedir-spec-') do |dir|
    old_path = Dir.pwd
    Dir.chdir(dir)
    yield
    Dir.chdir(old_path)
  end
end

RSpec.configure do |config|
  # Allows using build(), create(), etc. without the "FactoryGirl." part.
  config.include FactoryGirl::Syntax::Methods

  config.around(:each) do |example|
    within_a_tmpdir(&example)
  end
end
