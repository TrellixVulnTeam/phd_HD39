load("@io_bazel_rules_go//go:def.bzl", "go_binary", "go_library")

go_library(
    name = "go_default_library",
    srcs = ["main.go"],
    importpath = "github.com/ChrisCummins/phd/compilers/toy/util/print_ast",
    visibility = ["//visibility:private"],
    deps = [
        "//compilers/toy/lexer:go_default_library",
        "//compilers/toy/parser:go_default_library",
        "@com_github_golang_glog//:go_default_library",
    ],
)

go_binary(
    name = "print_ast",
    embed = [":go_default_library"],
    visibility = ["//visibility:public"],
)
