import os
from conans import ConanFile, CMake, tools

class QtkeychainConan(ConanFile):
    name = "qtkeychain"
    license = "Modified BSD license"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/frankosterfeld/qtkeychain"
    topics = ("conan", "Keychain", "passwords", "secret", "qt")
    description = "QtKeychain is a Qt API to store passwords and other secret data securely."
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "shared": [True, False],
        "with_cred_store": [True, False],
        "with_libsecret": [True, False],
        "fPIC": [True, False]
    }
    default_options = {"shared": False, "fPIC": True, "with_cred_store": True, "with_libsecret": True}
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    _cmake = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def config_options(self):
        if self.settings.os != "Linux":
            del self.options.with_libsecret
        if self.settings.os != "Windows":
            del self.options.with_cred_store

    #def requirements(self):
    #    self.requires("qt/5.15.1")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("qtkeychain-{}".format(self.version), self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        self._cmake = CMake(self)
        self._cmake.definitions['QTKEYCHAIN_STATIC'] = (self.options.shared == False)
        self._cmake.definitions['USE_CREDENTIAL_STORE'] = self.options.get_safe("with_cred_store", default=False)
        #self._cmake.definitions['ECM_MKSPECS_INSTALL_DIR'] = os.path.join(self.package_folder, "res", "mkspecs", "modules")
        #self._cmake.definitions['CMAKE_INSTALL_DATADIR'] = os.path.join(self.package_folder, "res")
        self._cmake.configure()
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy("COPYING", src=self._source_subfolder, dst="licenses")

    def package_info(self):
        self.cpp_info.libs = ["qt5keychain"]
        self.cpp_info.includedirs = ['include', 'include/qt5keychain']

