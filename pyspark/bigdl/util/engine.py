#
# Copyright 2016 The BigDL Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import sys
import os
import glob

def __prepare_spark_env():
    modules = sys.modules
    if "pyspark" not in modules or "py4j" not in modules:
        spark_home = os.environ.get('SPARK_HOME', None)
        if not spark_home:
            raise ValueError(
                """Could not find Spark. Pls make sure SPARK_HOME env is set:
                   export SPARK_HOME=path to your spark home directory""")
        print("Using %s" % spark_home)
        py4j = glob.glob(os.path.join(spark_home, 'python/lib', 'py4j-*.zip'))[0]
        pyspark = glob.glob(os.path.join(spark_home, 'python/lib', 'pyspark*.zip'))[0]
        sys.path.insert(0, py4j)
        sys.path.insert(0, pyspark)


def __prepare_bigdl_env():
    jar_dir = os.path.abspath(__file__ + "/../../")
    conf_paths = glob.glob(os.path.join(jar_dir, "share/conf/*.conf"))
    bigdl_classpath = get_bigdl_classpath()

    def append_path(env_var_name, path):
        try:
            print("Adding %s to %s" % (path, env_var_name))
            os.environ[env_var_name] = path + ":" + os.environ[
                env_var_name]  # noqa
        except KeyError:
            os.environ[env_var_name] = path

    if conf_paths:
        assert len(conf_paths) == 1, "Expecting one conf: %s" % len(conf_paths)
        print("Prepending %s to sys.path" % conf_paths[0])
        sys.path.insert(0, conf_paths[0])

    if bigdl_classpath and is_spark_below_2_2():
        append_path("SPARK_CLASSPATH", bigdl_classpath)


def get_bigdl_classpath():
    """
    Get and return the jar path for bigdl if exists.
    """
    if(os.getenv("BIGDL_CLASSPATH")):
        return os.environ["BIGDL_CLASSPATH"]
    jar_dir = os.path.abspath(__file__ + "/../../")
    jar_paths = glob.glob(os.path.join(jar_dir, "share/lib/*.jar"))
    if jar_paths:
        assert len(jar_paths) == 1, "Expecting one jar: %s" % len(jar_paths)
        return jar_paths[0]
    return ""


def is_spark_below_2_2():
    """
    Check if spark version is below 2.2
    """
    import pyspark
    if(hasattr(pyspark,"version")):
        full_version = pyspark.version.__version__
        # We only need the general spark version (eg, 1.6, 2.2).
        parts = full_version.split(".")
        spark_version = parts[0] + "." + parts[1]
        if(compare_version(spark_version, "2.2")>=0):
            return False
    return True


def compare_version(version1, version2):
    """
    Compare version strings.
    :param version1;
    :param version2;
    :return: 1 if version1 is after version2; -1 if version1 is before version2; 0 if two versions are the same.
    """
    v1Arr = version1.split(".")
    v2Arr = version2.split(".")
    len1 = len(v1Arr)
    len2 = len(v2Arr)
    lenMax = max(len1, len2)
    for x in range(lenMax):
        v1Token = 0
        if x < len1:
            v1Token = int(v1Arr[x])
        v2Token = 0
        if x < len2:
            v2Token = int(v2Arr[x])
        if v1Token < v2Token:
            return -1
        if v1Token > v2Token:
            return 1
    return 0


def prepare_env():
    __prepare_spark_env()
    __prepare_bigdl_env()