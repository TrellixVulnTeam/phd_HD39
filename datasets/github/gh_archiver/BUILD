# This package defines a utility script for mirroring a user's GitHub repos.
#
# Copyright 2017-2020 Chris Cummins <chrisc.101@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

load("@cec_exports_repo//tools/bzl:exports_repo.bzl", "exports_repo")
load("@com_github_chriscummins_rules_bats//:bats.bzl", "bats_test")
load("@subpar//:subpar.bzl", "par_binary")

exports_files([
    "LICENSE",
    "README.md",
    "CNAME",
])

exports_repo(
    name = "export",
    path_rename = {
        "datasets/github/gh_archiver/README.md": "README.md",
        "datasets/github/gh_archiver/LICENSE": "LICENSE",
    },
    remote = "git@github.com:ChrisCummins/gh-archiver.git",
    tags = ["manual"],
    targets = ["//datasets/github/gh_archiver/..."],
)

par_binary(
    name = "gh_archiver",
    srcs = ["gh_archiver.py"],
    deps = [
        "//datasets/github:api",
        "//labm8/py:app",
        "//third_party/py/git",
        "//third_party/py/github",
        "//tools/git:git_clone",
    ],
)

bats_test(
    name = "gh_archiver_par_test",
    srcs = ["gh_archiver_par_test.bats"],
    data = [
        ":gh_archiver.par",
        "//labm8/sh:test",
    ],
)

sh_binary(
    name = "install",
    srcs = ["install.sh"],
    data = [":gh_archiver.par"],
    deps = [
        "//labm8/sh:app",
    ],
)
