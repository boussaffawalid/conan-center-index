import os
from conans import ConanFile, CMake, tools


class O2Conan(ConanFile):
    name = "o2"
    license = "BSD 2-Clause \"Simplified\" License"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/pipacs/o2"
    topics = ("conan", "network", "OAuth", "qt")
    description = "This library encapsulates the OAuth 1.0 and 2.0 client authentication flows, and the sending of authenticated HTTP requests."
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_oauth1": [True, False],
        "with_keychain": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_oauth1": True,
        "with_keychain": True
    }
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def requirements(self):
        #self.requires("qt/5.15.1")
        if self.options.with_keychain:
            self.requires("qtkeychain/0.11.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("o2-{}".format(self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        _all_options = ['with_twitter', 'with_dropbox', 'with_google', 'with_vimeo', 
            'with_facebook','with_uber', 'with_skydrive', 'with_flickr', 'with_spotify', 
            'with_smugmug', 'with_msgraph', 'with_keychain']

        self._cmake = CMake(self)
        self._cmake.definitions['o2_WITH_OAUTH1'] = self.options.with_oauth1
        self._cmake.definitions['o2_WITH_KEYCHAIN'] = self.options.with_keychain
        for option in _all_options:
            self._cmake.definitions['o2_{}'.format(option.upper())] = True
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")
        self.copy("o0export.h", src=os.path.join(self._source_subfolder, "src"), dst="include/o2")

    def package_info(self):
        self.cpp_info.libs = ["o2"]
        self.cpp_info.includedirs = ['include', "include/o2"]

