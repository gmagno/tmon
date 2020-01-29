#!/bin/bash
set -e -x

export PYHOME=/home
cd ${PYHOME}

/opt/python/cp37-cp37m/bin/pip install twine cmake
ln -s /opt/python/cp37-cp37m/bin/cmake /usr/bin/cmake

# Compile wheels
for PYBIN in /opt/python/cp3*/bin; do
    "${PYBIN}/pip" wheel /io/ -w wheelhouse/
    "${PYBIN}/python" /io/setup.py sdist -d /io/wheelhouse/
done

# Bundle external shared libraries into the wheels
for whl in wheelhouse/*.whl; do
    auditwheel repair "$whl" -w /io/wheelhouse/
done

# Test
for PYBIN in /opt/python/cp3*/bin/; do
    "${PYBIN}/pip" install -r /io/requirements-test.txt
    "${PYBIN}/pip" install --no-index -f /io/wheelhouse nb-cpp
    (cd "$PYHOME"; "${PYBIN}/pytest" /io/test/)
done

#  Upload
for WHEEL in /io/wheelhouse/nb_cpp*; do
    # dev
    # /opt/python/cp37-cp37m/bin/twine upload \
    #     --skip-existing \
    #     --repository-url https://test.pypi.org/legacy/ \
    #     -u "${TWINE_USERNAME}" -p "${TWINE_PASSWORD}" \
    #     "${WHEEL}"
    # prod
    /opt/python/cp37-cp37m/bin/twine upload \
        --skip-existing \
        -u "${TWINE_USERNAME}" -p "${TWINE_PASSWORD}" \
        "${WHEEL}"
done
