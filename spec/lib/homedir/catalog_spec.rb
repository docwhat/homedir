require 'spec_helper'
require 'homedir/catalog'
require 'homedir/errors'


describe Homedir::Catalog do
  def mkpkg(name, dependencies=[])
    double(name).tap do |pkg|
      pkg.stub(:name) { name }
      pkg.stub(:dependencies) { dependencies }
    end
  end

  describe ".add" do
    it "adds the package to the catalog" do
      pkg = mkpkg('somename')
      subject.add pkg
      subject.should include(pkg)
    end
  end

  describe ".find_all_dependencies" do
    let(:pkg) { mkpkg('pkg', ['pkg2']) }

    context "in an acyclic graph" do
      before(:each) do
        subject.add mkpkg('pkg2', ['pkg3'])
        subject.add mkpkg('pkg3')
        subject.add mkpkg('lonelypkg')
      end

      it "should all dependencies" do
        dependents = subject.find_all_dependencies(pkg)
        dependents.size.should == 3
      end

      it "should be packages" do
        dependents = subject.find_all_dependencies(pkg)
        dependents.each do |p|
          p.should respond_to(:name)
        end
      end
    end

    context "in a cyclic graph" do
      before(:each) do
        subject.add pkg
        subject.add mkpkg('pkg2', [pkg.name])
      end

      it "should return only two" do
        dependents = subject.find_all_dependencies(pkg)
        dependents.size.should == 2
      end
    end

    context "with a missing dependency" do
      it "should raise an error" do
        expect { subject.find_all_dependencies(pkg) }.to raise_error(Homedir::MissingDependencyError)
      end
    end
  end

  describe ".find_by_name" do
    let(:pkg) { mkpkg('a-name') }
    before(:each) do
      subject.add(pkg)
    end

    it "return pkg" do
      subject.find_by_name(pkg.name).should == pkg
    end
  end
end

