require 'spec_helper'
require 'homedir/package'
require 'homedir/catalog'

describe "Cataloging Packages" do
  let(:catalog) { Homedir::Catalog.new }

  context "with an empty catalog" do
    it "a package can be added" do
      catalog.add Homedir::Package.new :name => 'name1'
      catalog.size.should == 1
    end
  end

  context "a full catalog" do
    before(:each) do
      (1..10).each do |i|
        catalog.add Homedir::Package.new :name => "name#{i}"
      end
    end
    it "a package can be found" do
      pkg = catalog.find_by_name "name3"
      pkg.should be
    end
  end

end
