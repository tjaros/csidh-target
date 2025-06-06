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


# Executable
add_executable(main main.c)

# Link the executable with the shared library
target_link_libraries(main PRIVATE csidh)

# Install targets
install(TARGETS csidh DESTINATION .)
install(TARGETS main DESTINATION .)

