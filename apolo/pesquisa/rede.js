// Defesa contra SSRF: o navegador só pode ir a endereços públicos, nunca à rede interna (banco, córtex, localhost...).
import dns from 'node:dns/promises';
import net from 'node:net';

function ipv4Publico(ip) {
  const [a, b] = ip.split('.').map(Number);
  if (a === 0 || a === 10 || a === 127 || a >= 224) return false;
  if (a === 100 && b >= 64 && b <= 127) return false; // CGNAT
  if (a === 169 && b === 254) return false; // link-local / metadados de nuvem
  if (a === 172 && b >= 16 && b <= 31) return false;
  if (a === 192 && (b === 168 || (b === 0 && ip.startsWith('192.0.0.')))) return false;
  if (a === 198 && (b === 18 || b === 19)) return false;
  return true;
}

export function ipPublico(ip) {
  if (net.isIPv4(ip)) return ipv4Publico(ip);
  if (net.isIPv6(ip)) {
    const baixo = ip.toLowerCase();
    const mapeado = baixo.match(/^::ffff:(\d+\.\d+\.\d+\.\d+)$/);
    if (mapeado) return ipv4Publico(mapeado[1]);
    if (baixo === '::' || baixo === '::1') return false;
    return !/^(fc|fd|fe[89ab])/.test(baixo);
  }
  return false;
}

export async function urlPermitida(texto, resolver = (h) => dns.lookup(h, { all: true })) {
  let url;
  try {
    url = new URL(texto);
  } catch {
    return false;
  }
  if (url.protocol !== 'http:' && url.protocol !== 'https:') return false;
  const host = url.hostname.replace(/^\[|\]$/g, '');
  if (net.isIP(host)) return ipPublico(host);
  try {
    const enderecos = await resolver(host);
    return enderecos.length > 0 && enderecos.every((e) => ipPublico(e.address));
  } catch {
    return false;
  }
}
