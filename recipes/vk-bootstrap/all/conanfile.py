from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd, stdcpp_library
from conan.tools.cmake import CMake, CMakeToolchain, CMakeDeps, cmake_layout
from conan.tools.files import copy, get, rm, replace_in_file
from conan.tools.microsoft import is_msvc
from conan.tools.scm import Version
import os

required_conan_version = ">=1.54.0"


class VkBootstrapConan(ConanFile):
    name = "vk-bootstrap"
    description = "Vulkan bootstraping library."
    license = "MIT"
    topics = ("vulkan", "bootstrap", "setup")
    homepage = "https://github.com/charles-lunarg/vk-bootstrap"
    url = "https://github.com/conan-io/conan-center-index"

    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
    }

    @property
    def _min_cppstd(self):
        return "17" if Version(self.version) >= "1.3.270" else "14"

    @property
    def _compilers_minimum_version(self):
        return {
            "gcc": "5",
            "Visual Studio": "15",
            "msvc": "191",
            "clang": "3.7" if stdcpp_library(self) == "stdc++" else "6",
            "apple-clang": "10",
        }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.get_safe("shared"):
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if Version(self.version) > Version("1.0"):
            self.requires(f"vulkan-headers/{self.version}.0", transitive_headers=True)
        else:
            self.requires("vulkan-headers/1.3.239.0", transitive_headers=True)

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

        def loose_lt_semver(v1, v2):
            lv1 = [int(v) for v in v1.split(".")]
            lv2 = [int(v) for v in v2.split(".")]
            min_length = min(len(lv1), len(lv2))
            return lv1[:min_length] < lv2[:min_length]

        minimum_version = self._compilers_minimum_version.get(str(self.settings.compiler), False)
        if minimum_version and loose_lt_semver(str(self.settings.compiler.version), minimum_version):
            raise ConanInvalidConfiguration(
                f"{self.ref} requires C++{self._min_cppstd}, which your compiler does not support.",
            )

        if is_msvc(self) and self.options.get_safe("shared"):
            raise ConanInvalidConfiguration(f"{self.ref} shared not supported with Visual Studio")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["VK_BOOTSTRAP_TEST"] = False
        tc.variables["VK_BOOTSTRAP_WERROR"] = False
        if Version(self.version) < Version("1.0"):
            vulkan_headers = self.dependencies["vulkan-headers"]
            includedirs = ";".join(
                [os.path.join(vulkan_headers.package_folder, includedir).replace("\\", "/")
                for includedir in vulkan_headers.cpp_info.includedirs],
            )
            tc.variables["VK_BOOTSTRAP_VULKAN_HEADER_DIR"] = includedirs
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def _source_patches(self):
        if Version(self.version) >= "1.3.266":
            # INFO: The upstream did not forbid the use of shared libraries
            # https://github.com/charles-lunarg/vk-bootstrap/issues/367
            replace_in_file(self, os.path.join(self.source_folder, "CMakeLists.txt"),
                            "add_library(vk-bootstrap STATIC",
                            "add_library(vk-bootstrap ")

    def build(self):
        self._source_patches()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rm(self, "*", os.path.join(self.package_folder, "lib", "cmake"), recursive=True)

    def package_info(self):
        self.cpp_info.libs = ["vk-bootstrap"]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["dl"]
