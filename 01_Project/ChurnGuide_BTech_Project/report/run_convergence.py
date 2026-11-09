import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import report.build_report as br
import fitz

styles = br.get_styles()

registry = {}
end_registry = {}

output_pdf = 'report/test_converge.pdf'

for pass_idx in range(1, 5):
    print(f"\n--- PASS {pass_idx} ---")
    prev_end = dict(end_registry)
    
    # We clear registry and end_registry so the Trackers populate fresh values for this pass
    doc = br.SimpleDocTemplate(
        output_pdf,
        pagesize=br.A4,
        leftMargin=br.MARGIN_LEFT,
        rightMargin=br.MARGIN_RIGHT,
        topMargin=br.MARGIN_TOP,
        bottomMargin=br.MARGIN_BOTTOM
    )
    # Notice: we pass prev_end for odd_transition so it knows parities from the previous pass!
    # And we pass registry so TOC can read page numbers from the previous pass!
    # But wait! If registry is cleared, where do TOC and odd_transition read from?
    # They should read from the previous pass snapshot!
    pass_story = br.build_full_story(styles, registry, prev_end)
    doc.build(pass_story, canvasmaker=br.ReportCanvas)
    
    total = len(fitz.open(output_pdf))
    print(f"Pass {pass_idx} finished. Total pages: {total}")
    print(f"CH1: {registry.get('CH1')} | CH2: {registry.get('CH2')} | CH3: {registry.get('CH3')} | CH4: {registry.get('CH4')}")
    print(f"CH5: {registry.get('CH5')} | CH6: {registry.get('CH6')} | CH7: {registry.get('CH7')} | REF: {registry.get('REFERENCES')}")
    
    if prev_end == end_registry:
        print(f"*** CONVERGED AT PASS {pass_idx}! ***")
        break

