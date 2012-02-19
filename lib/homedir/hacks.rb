require 'fileutils'
require 'pathname'

class Pathname
  def mkdir_p *args
    FileUtils.mkdir_p(self.to_s, *args)
  end
end
