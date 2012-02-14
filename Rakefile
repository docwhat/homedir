#!/usr/bin/env rake
require "bundler/gem_tasks"
require 'rspec/core/rake_task'

desc "Run all specs"
RSpec::Core::RakeTask.new(:spec) do |t|
  t.pattern = "spec/**/*_spec.rb"
end
task :default => :spec

desc "Travis-CI Tests"
task :travis do
  Rake::Task["spec"].invoke
end
