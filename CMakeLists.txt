cmake_minimum_required(VERSION 3.18)
project(ApexLOB LANGUAGES CXX CUDA)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CUDA_STANDARD 17)

# Fetch pybind11 automatically
include(FetchContent)
FetchContent_Declare(
  pybind11
  GIT_REPOSITORY https://github.com/pybind/pybind11.git
  GIT_TAG        v2.12.0
)
FetchContent_MakeAvailable(pybind11)

# UPDATE: Point CMake to the new 'src/' subdirectory paths
pybind11_add_module(apex_lob 
    src/main.cpp 
    src/risk_engine.cu
)

# UPDATE: Tell the compiler where the public 'include/' headers live
target_include_directories(apex_lob PRIVATE include)

# Link the CUDA toolkit libraries for the RTX 3090
set_target_properties(apex_lob PROPERTIES CUDA_ARCHITECTURES "86")
target_compile_features(apex_lob PUBLIC cxx_std_20)

# Apply hardware-level AVX-512 flags ONLY to the standard C++ compiler
if(MSVC)
    target_compile_options(apex_lob PRIVATE $<$<COMPILE_LANGUAGE:CXX>:/O2;/arch:AVX512>)
else()
    target_compile_options(apex_lob PRIVATE $<$<COMPILE_LANGUAGE:CXX>:-O3;-march=native;-mavx512f>)
endif()