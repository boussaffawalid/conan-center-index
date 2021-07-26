from conans import ConanFile, tools, AutoToolsBuildEnvironment, MSBuild
from conans.errors import ConanInvalidConfiguration
import os


class LibmadConan(ConanFile):
    name = "libmad"
    description = "MAD is a high-quality MPEG audio decoder.format."
    topics = ("conan", "mad", "MPEG", "audio", "decoder")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://www.underbit.com/products/mad/"
    license = "GPL-2.0-or-later"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd
        if self.options.shared:
            del self.options.fPIC
 
    def validate(self):
        if self.options.shared and self._is_msvc:
            raise ConanInvalidConfiguration("libmad does not support shared library for MSVC")
        if (self.settings.os == "Macos" and self.settings.arch == "armv8"
                and hasattr(self, 'settings_build') 
                and tools.cross_building(self, skip_x64_x86=True)):
            raise ConanInvalidConfiguration("Cross-building for Macos to armv8 not implemented")
            
    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    def build(self):
        if self._is_msvc:
            self._build_msvc()
        else:
            self._build_configure()

    def _build_msvc(self):
        with tools.chdir(os.path.join(self._source_subfolder, "msvc++")):
            # cl : Command line error D8016: '/ZI' and '/Gy-' command-line options are incompatible
            tools.replace_in_file("libmad.dsp", "/ZI ", "")
            if self.settings.arch == "x86_64":
                tools.replace_in_file("libmad.dsp", "Win32", "x64")
                tools.replace_in_file("libmad.dsp", "FPM_INTEL", "FPM_DEFAULT")
                tools.replace_in_file("mad.h", "# define FPM_INTEL", "# define FPM_DEFAULT")
            with tools.vcvars(self.settings):
                self.run("devenv libmad.dsp /upgrade")
            msbuild = MSBuild(self)
            msbuild.build(project_file="libmad.vcxproj")

    def _build_configure(self):
        with tools.chdir(self._source_subfolder):
            if self.options.shared:
                args = ["--disable-static", "--enable-shared"]
            else:
                args = ["--disable-shared", "--enable-static"]
            env_build = AutoToolsBuildEnvironment(self)
            env_build.configure(args=args)
            env_build.make()
            env_build.install()
            la = os.path.join(self.package_folder, "lib", "libmad.la")
            if os.path.isfile(la):
                os.unlink(la)

    def package(self):
        self.copy("COPYRIGHT", dst="licenses", src=self._source_subfolder)
        self.copy("COPYING", dst="licenses", src=self._source_subfolder)
        self.copy("CREDITS", dst="licenses", src=self._source_subfolder)
        if self._is_msvc:
            self.copy(pattern="*.lib", dst="lib", src=self._source_subfolder, keep_path=False)
            self.copy(pattern="mad.h", dst="include", src=os.path.join(self._source_subfolder, "msvc++"))

    def package_info(self):
        self.cpp_info.libs = ["libmad" if self._is_msvc else "mad"]
