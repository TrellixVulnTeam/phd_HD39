py_library(
    name = "ast_smoke_test",
    testonly = 1,
    srcs = ["ast_smoke_test.py"],
    data = [
        "//compilers/toy:test_data",
        "//compilers/toy/util/print_ast",
    ],
    deps = [
        "//compilers/toy/tests:smoke_test_flags",
        "//labm8/py:app",
        "//labm8/py:bazelutil",
        "//labm8/py:fs",
        "//labm8/py:test",
    ],
)

py_test(
    name = "ast_smoke_test_stage1",
    srcs = ["ast_smoke_test.py"],
    args = [
        "--stage",
        "1",
    ],
    main = "ast_smoke_test.py",
    deps = [":ast_smoke_test"],
)

py_test(
    name = "ast_smoke_test_stage2",
    srcs = ["ast_smoke_test.py"],
    args = [
        "--stage",
        "2",
    ],
    main = "ast_smoke_test.py",
    deps = [":ast_smoke_test"],
)

py_test(
    name = "ast_smoke_test_stage3",
    srcs = ["ast_smoke_test.py"],
    args = [
        "--stage",
        "3",
    ],
    main = "ast_smoke_test.py",
    deps = [":ast_smoke_test"],
)

py_test(
    name = "ast_smoke_test_stage4",
    srcs = ["ast_smoke_test.py"],
    args = [
        "--stage",
        "4",
    ],
    main = "ast_smoke_test.py",
    deps = [":ast_smoke_test"],
)

py_test(
    name = "ast_smoke_test_stage5",
    srcs = ["ast_smoke_test.py"],
    args = [
        "--stage",
        "5",
        "--xfail",
    ],
    main = "ast_smoke_test.py",
    deps = [":ast_smoke_test"],
)

py_test(
    name = "ast_smoke_test_stage6",
    srcs = ["ast_smoke_test.py"],
    args = [
        "--stage",
        "6",
        "--xfail",
    ],
    main = "ast_smoke_test.py",
    deps = [":ast_smoke_test"],
)

py_test(
    name = "ast_smoke_test_stage7",
    srcs = ["ast_smoke_test.py"],
    args = [
        "--stage",
        "7",
        "--xfail",
    ],
    main = "ast_smoke_test.py",
    deps = [":ast_smoke_test"],
)

py_test(
    name = "ast_smoke_test_stage8",
    srcs = ["ast_smoke_test.py"],
    args = [
        "--stage",
        "8",
        "--xfail",
    ],
    main = "ast_smoke_test.py",
    deps = [":ast_smoke_test"],
)

py_test(
    name = "ast_smoke_test_stage9",
    srcs = ["ast_smoke_test.py"],
    args = [
        "--stage",
        "9",
        "--xfail",
    ],
    main = "ast_smoke_test.py",
    deps = [":ast_smoke_test"],
)

py_test(
    name = "ast_smoke_test_stage10",
    srcs = ["ast_smoke_test.py"],
    args = [
        "--stage",
        "10",
        "--xfail",
    ],
    main = "ast_smoke_test.py",
    deps = [":ast_smoke_test"],
)
