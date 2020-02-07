#!/bin/bash
set -e -x

export PYHOME=/io/
cd ${PYHOME}

ln -s /opt/python/cp35-cp35m/bin/python /usr/local/bin/python3.5
ln -s /opt/python/cp36-cp36m/bin/python /usr/local/bin/python3.6
ln -s /opt/python/cp37-cp37m/bin/python /usr/local/bin/python3.7
ln -s /opt/python/cp38-cp38/bin/python /usr/local/bin/python3.8

python3.8 -m pip install -U pip
python3.8 -m pip install -r requirements_dev.txt
python3.8 -m pip install twine

# Compile wheels
for PYBIN in /opt/python/cp3{5,6,7,8}*/bin; do
    "${PYBIN}/pip" install -U pip
    "${PYBIN}/pip" wheel /io/ -w wheelhouse/
    "${PYBIN}/python" /io/setup.py sdist -d /io/wheelhouse/
done

# Bundle external shared libraries into the wheels
for whl in wheelhouse/*.whl; do
    auditwheel repair "$whl" -w /io/wheelhouse/
done

# Test
python3.8 -m tox

#  Upload
for WHEEL in /io/wheelhouse/tmon*; do
    # dev
    # /opt/python/cp38-cp38m/bin/twine upload \
    #     --skip-existing \
    #     --repository-url https://test.pypi.org/legacy/ \
    #     -u "${TWINE_USERNAME}" -p "${TWINE_PASSWORD}" \
    #     "${WHEEL}"
    # prod
    /opt/python/cp38-cp38m/bin/twine upload \
        --skip-existing \
        -u "${TWINE_USERNAME}" -p "${TWINE_PASSWORD}" \
        "${WHEEL}"
done
