import numpy

def lanczos(n):
    x = numpy.linspace(0, n, 8192, endpoint=False)
    phi = numpy.sinc(x) * numpy.sinc(x/n)
    sum = 2 * numpy.trapz(phi, x)
    phi /= sum
    return phi, x

def genlanczos(n):
    phi, x = lanczos(n)
    name = 'lanczos%d' % n
    support = 2 * n

    vnumbers = ["%.8f, %.8f, %.8f, %.8f" % tuple(a) for a in phi.reshape(-1, 4)]
    step = numpy.diff(x).mean()

    template = """
    static double _%(funcname)s_vtable[] = %(vtable)s;
    static double _%(funcname)s_nativesupport = %(support)g;
    static double _%(funcname)s_kernel(double x)
    {
        x = fabs(x);
        double f = x / %(step)e;
        int i = f;
        if (i < 0) return 0;
        if (i >= %(tablesize)d - 1) return 0;
        f -= i;
        return _%(funcname)s_vtable[i] * (1 - f)
             + _%(funcname)s_vtable[i+1] * f;
    }
    static double _%(funcname)s_diff(double x)
    {
        double factor;
        if(x >= 0) {
            factor = 1;
        } else {
            factor = -1;
            x = -x;
        }

        int i = x / %(step)e;
        if (i < 0) return 0;
        if (i >= %(tablesize)d - 1) return 0;
        double f = _%(funcname)s_vtable[i+1] - _%(funcname)s_vtable[i];
        return factor * f / %(step)e;
    }
    """
    return template % {
            'vtable' : "{" + ",\n".join(vnumbers) + "}",
            'hsupport' : support * 0.5,
            'support' : support,
            'funcname' : name,
            'step' : step,
            'tablesize' : len(phi),
    }

with open('pmesh/_window_lanczos.h', 'wt') as f:
    f.write(genlanczos(2))
    f.write(genlanczos(3))
