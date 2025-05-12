cmake_minimum_required(VERSION 3.10)

project(csidh)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 11)

add_compile_options(-Wall -Wextra -O0 -DF419 -g)

add_library(csidh SHARED
	csidh.c
	fp.c
	mont.c
	randombytes.c
	uint.c
	parametrization.c
)

install(TARGETS csidh DESTINATION .)
