// Tweaks panel for CFLD — exposes typo system swap
const { useState, useEffect } = React;

function CFLDTweaks() {
  const initialTypo = (() => {
    try { return localStorage.getItem('cfld-typo') || 'editorial'; }
    catch(e) { return 'editorial'; }
  })();
  const [t, setTweak] = useTweaks({ typo: initialTypo });

  useEffect(() => {
    document.documentElement.setAttribute('data-typo', t.typo);
    try { localStorage.setItem('cfld-typo', t.typo); } catch(e) {}
  }, [t.typo]);

  return (
    <TweaksPanel title="Tweaks">
      <TweakSection title="Système typographique">
        <TweakRadio
          label="Style"
          value={t.typo}
          onChange={(v) => setTweak('typo', v)}
          options={[
            { value: 'editorial', label: 'Éditorial' },
            { value: 'modern', label: 'Modern' },
            { value: 'sporty', label: 'Sporty' },
          ]}
        />
        <p style={{
          fontSize: 12, color: 'rgba(11,11,11,0.55)',
          fontFamily: 'ui-monospace, Menlo, monospace',
          margin: '8px 0 0', lineHeight: 1.5
        }}>
          Éditorial = serif premium (Fraunces) · Modern = sans géométrique (Space Grotesk) · Sporty = display condensé (Bebas Neue)
        </p>
      </TweakSection>
    </TweaksPanel>
  );
}

const root = document.getElementById('tweaks-root') || (() => {
  const el = document.createElement('div');
  el.id = 'tweaks-root';
  document.body.appendChild(el);
  return el;
})();
ReactDOM.createRoot(root).render(<CFLDTweaks />);
