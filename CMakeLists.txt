cmake_minimum_required(VERSION 3.18)
project(ApexLOB LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Unlock AVX-512 Hardware Vectorization for MSVC (Windows)
if(MSVC)
    add_compile_options(/O2 /arch:AVX512)
else()
    add_compile_options(-O3 -march=native -mavx512f)
endif()

include(FetchContent)
FetchContent_Declare(
  pybind11
  GIT_REPOSITORY https://github.com/pybind/pybind11.git
  GIT_TAG        v2.12.0
)
FetchContent_MakeAvailable(pybind11)

# Compile into a Python-importable module named apex_lob
pybind11_add_module(apex_lob main.cpp)