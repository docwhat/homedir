require 'spec_helper'
require 'homedir'


describe "Loading packages" do
  context "with a fake set of packages" do
    before(:each) do
      make_package_v1("version1")
      make_package_v2("version2")
      make_package_v3("version3")
    end

    it "can read all packages" do
      pending "Work In Progress"
      catalog = Homedir::Catalog.new
      catalog.load(TEST_DIR)
      catalog.length.should == 3
      names = catalog.map { |p| p.name }
      names.should include("version1")
      names.should include("version2")
      names.should include("version3")
    end

  end
end
