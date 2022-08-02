# -*- coding: utf-8 -*-

"""
trace/generated-tracers.h
"""

__author__     = "Lluís Vilanova <vilanova@ac.upc.edu>"
__copyright__  = "Copyright 2012-2017, Lluís Vilanova <vilanova@ac.upc.edu>"
__license__    = "GPL version 2 or (at your option) any later version"

__maintainer__ = "Stefan Hajnoczi"
__email__      = "stefanha@redhat.com"


from tracetool import out


def generate(events, backend, group):
    header = "trace/control-vcpu.h" if group == "root" else "trace/control.h"
    out(
        '/* This file is autogenerated by tracetool, do not edit. */',
        '',
        f'#ifndef TRACE_{group.upper()}_GENERATED_TRACERS_H',
        f'#define TRACE_{group.upper()}_GENERATED_TRACERS_H',
        '',
        '#include "%s"' % header,
        '',
    )


    for e in events:
        out('extern TraceEvent %(event)s;',
            event = e.api(e.QEMU_EVENT))

    for e in events:
        out(f'extern uint16_t {e.api(e.QEMU_DSTATE)};')

    # static state
    for e in events:
        enabled = 0 if 'disable' in e.properties else 1
        if "tcg-exec" in e.properties:
            # a single define for the two "sub-events"
            out('#define TRACE_%(name)s_ENABLED %(enabled)d',
                name=e.original.name.upper(),
                enabled=enabled)
        out('#define TRACE_%s_ENABLED %d' % (e.name.upper(), enabled))

    backend.generate_begin(events, group)

    for e in events:
        # tracer-specific dstate
        out('',
            '#define %(api)s() ( \\',
            api=e.api(e.QEMU_BACKEND_DSTATE))

        if "disable" not in e.properties:
            backend.generate_backend_dstate(e, group)

        out('    false)')

        # tracer without checks
        out('',
            'static inline void %(api)s(%(args)s)',
            '{',
            api=e.api(e.QEMU_TRACE_NOCHECK),
            args=e.args)

        if "disable" not in e.properties:
            backend.generate(e, group)

        out('}')

        # tracer wrapper with checks (per-vCPU tracing)
        if "vcpu" in e.properties:
            trace_cpu = next(iter(e.args))[1]
            cond = "trace_event_get_vcpu_state(%(cpu)s,"\
                   " TRACE_%(id)s)"\
                   % dict(
                       cpu=trace_cpu,
                       id=e.name.upper())
        else:
            cond = "true"

        out('',
            'static inline void %(api)s(%(args)s)',
            '{',
            '    if (%(cond)s) {',
            '        %(api_nocheck)s(%(names)s);',
            '    }',
            '}',
            api=e.api(),
            api_nocheck=e.api(e.QEMU_TRACE_NOCHECK),
            args=e.args,
            names=", ".join(e.args.names()),
            cond=cond)

    backend.generate_end(events, group)

    out(f'#endif /* TRACE_{group.upper()}_GENERATED_TRACERS_H */')
