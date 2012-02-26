# Guardfile
# More info at https://github.com/guard/guard#readme

guard 'bundler' do
  watch('Gemfile')
  # Uncomment next line if Gemfile contain `gemspec' command
  # watch(/^.+\.gemspec/)
end

guard 'rspec', :version => 2, :cli => "--color --format doc" do
  watch(%r{^spec/.+_spec\.rb$})
  watch(%r{^lib/})                 { "spec/integration" }
  #watch(%r{^(lib|bin)/})           { "spec/acceptance" }
  watch(%r{^lib/(.+)\.rb$})        { |m| "spec/lib/#{m[1]}_spec.rb" }
  watch('spec/spec_helper.rb')     { "spec" }
  watch('spec/factories.rb')       { "spec" }
  watch(%r{^spec/support/.+\.rb})  { "spec" }
  watch(%r{^spec/examples/})       { "spec" }
end


