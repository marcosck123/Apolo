import assert from 'node:assert/strict';
import { test } from 'node:test';
import { criarBuscadorDeCodigos, criarExecutor, criarRespostaDeCodigo, ehPerguntaDeProgramacao, filtrarCodigo } from '../src/codigo.js';
import { coletarCodigos, limparBloco } from '../pesquisa/codigos.js';
import { responderDaMemoria } from '../src/raciocinio.js';
import { criarApolo } from '../src/apolo.js';

const candidato = { linguagem: 'python', codigo: 'print(2 + 2)', fonte: 'https://www.exemplo.com/python' };

test('programação: termos fortes ativam, palavras comuns isoladas não', () => {
  for (const mensagem of ['Como somar em Python?', 'código de exemplo', 'função para somar', 'git status', 'programa em C', 'Docker', 'consulta SQL', 'javascript']) assert.ok(ehPerguntaDeProgramacao(mensagem), mensagem);
  for (const mensagem of ['lista de compras', 'for', 'erro', 'como fazer bolo?', 'qual a capital?']) assert.equal(ehPerguntaDeProgramacao(mensagem), false, mensagem);
});

test('filtro: bloqueia operações suspeitas e aceita entradas somente quando simuladas', () => {
  for (const codigo of ['os.system("x")', 'import subprocess', 'import socket', 'shutil.rmtree("x")', 'os.remove("x")', 'os.unlink("x")', 'open("/etc/passwd")', 'open("C:\\dados")', '__import__("os")', 'eval("1")', 'exec("1")', 'import requests', 'import urllib', 'import http.client', 'import os\nprint(os.environ)', 'import ctypes', 'input()']) assert.equal(filtrarCodigo(codigo).ok, false, codigo);
  assert.ok(filtrarCodigo('print(sum([1, 2]))').ok);
  assert.ok(filtrarCodigo('print(input())', { entradas: ['oi'] }).ok);
});

test('clientes: corpo, rota e falhas opcionais', async () => {
  const pedidos = [];
  const fetchFn = async (url, opcoes) => {
    pedidos.push([String(url), JSON.parse(opcoes.body)]);
    return { ok: true, json: async () => ({ codigos: [candidato], saida: '4', erro: '' }) };
  };
  assert.deepEqual(await criarBuscadorDeCodigos({ url: 'http://pesquisa', fetchFn })('somar'), [candidato]);
  await criarExecutor({ url: 'http://executor', fetchFn })({ linguagem: 'python', codigo: 'print(4)' });
  assert.equal(pedidos[0][0], 'http://pesquisa/codigos');
  assert.deepEqual(pedidos[0][1], { consulta: 'somar', max_paginas: 3 });
  assert.equal(pedidos[1][0], 'http://executor/executar');
  for (const criar of [criarExecutor, criarBuscadorDeCodigos]) {
    assert.equal(criar({ url: '' }), null);
    for (const fetchFn of [async () => { throw new Error('offline'); }, async () => ({ ok: false })]) assert.equal(await criar({ url: 'http://servico', fetchFn })('x'), null);
  }
});

test('código: ignora rejeitados, erros e saída vazia; guarda apenas o primeiro sucesso com origem', async () => {
  const lembrados = [], eventos = [], executados = [];
  const responder = criarRespostaDeCodigo({
    buscar: async () => [{ ...candidato, codigo: 'eval("1")' }, { ...candidato, codigo: 'print(0)' }, { ...candidato, codigo: 'pass' }, candidato],
    executar: async (pedido) => {
      executados.push(pedido);
      return pedido.codigo === 'print(0)' ? { erro: 'falhou', saida: '0' } : { erro: '', saida: pedido.codigo === 'pass' ? '' : '4\n', tempo_ms: 10 };
    },
    lembrar: async (n) => lembrados.push(n), registrar: (...evento) => eventos.push(evento),
  });
  const resposta = await responder('Como somar em Python?');
  assert.match(resposta, /Exemplo:\nprint\(2 \+ 2\)\nSaída:\n4/);
  assert.match(resposta, /fonte: exemplo.com/);
  assert.equal(executados.length, 3);
  assert.equal(lembrados.length, 1);
  assert.equal(lembrados[0].origem, 'executor');
  assert.equal(lembrados[0].tipo, 'habilidade');
  assert.match(lembrados[0].conteudo, /https:\/\/www.exemplo.com\/python/);
  assert.equal(eventos[0][0], 'codigo');
});

test('código: máximo de cinco candidatos e falhas honestas sem gravar', async () => {
  let tentativas = 0;
  const lembrar = async () => assert.fail('não deve gravar');
  const responder = criarRespostaDeCodigo({ buscar: async () => Array(8).fill(candidato), executar: async () => { tentativas++; return { erro: '', saida: '4', estourou_tempo: true }; }, lembrar });
  assert.equal(await responder('python'), null);
  assert.equal(tentativas, 5);
  for (const buscar of [null, async () => null, async () => { throw new Error('offline'); }, async () => [candidato]]) {
    assert.match(await criarRespostaDeCodigo({ buscar, executar: async () => null, lembrar })('python'), /indisponível|consegui/);
  }
});

test('limpeza: REPL remove saída, preserva indentação; blocos normais e limites', () => {
  assert.equal(limparBloco('>>> for n in [1, 2]:\n...     print(n)\n... \n1\n2'), 'for n in [1, 2]:\n    print(n)');
  assert.equal(limparBloco('$ python exemplo.py'), 'python exemplo.py');
  assert.equal(limparBloco('for n in [1]:\n    print(n)'), 'for n in [1]:\n    print(n)');
  assert.equal(limparBloco('x'.repeat(20_001)), '');
});

test('extração: consulta Python, deduplicação, páginas falhas e linguagens explícitas', async () => {
  let consulta;
  const codigos = await coletarCodigos('somar', {
    pesquisar: async (texto) => { consulta = texto; return [{ url: 'a' }, { url: 'b' }]; },
    lerBlocos: async (url) => {
      if (url === 'b') throw new Error('bloqueada');
      return { url: 'https://exemplo.com', blocos: [
        { texto: 'print(4)', linguagem: 'python', explicacao: 'Soma' },
        { texto: 'print(4)', linguagem: '', explicacao: '' },
        { texto: 'console.log(4)', linguagem: 'javascript', explicacao: '' },
      ] };
    },
  });
  assert.equal(consulta, 'somar python');
  assert.equal(codigos.length, 1);
  assert.equal(codigos[0].fonte, 'https://exemplo.com');
});

test('memória: habilidade conserva código, saída, fonte e todas as linhas', () => {
  const conteudo = 'Como somar em Python?\nExemplo:\nprint(4)\nSaída:\n4\n(fonte: https://exemplo.com)';
  assert.deepEqual(responderDaMemoria({ mensagem: 'Como somar em Python?', memoria: [{ id: 7, tipo: 'habilidade', conteudo }] }), { neuronioId: 7, resposta: conteudo });
  assert.equal(responderDaMemoria({ mensagem: 'Qual a capital da França?', memoria: [{ id: 7, tipo: 'habilidade', conteudo }] }), null);
});

test('lembrar: repassa origem e usa usuario por padrão', async () => {
  const criados = [];
  const repo = { similares: async () => [], salvarSinapses: async () => {}, criarNeuronio: async (n) => { criados.push(n); return { id: criados.length, ...n }; } };
  const apolo = criarApolo({ repo, embutirTexto: () => [1] });
  await apolo.lembrar({ conteudo: 'manual' });
  await apolo.lembrar({ conteudo: 'pesquisado', origem: 'web' });
  assert.deepEqual(criados.map((n) => n.origem), ['usuario', 'web']);
});

test('filtrarCodigo: __name__ e __main__ comuns passam, mas escapes por atributos especiais não', () => {
  assert.equal(filtrarCodigo('def f():\n    return 1\nif __name__ == "__main__":\n    print(f())').ok, true);
  assert.equal(filtrarCodigo('print(().__class__.__bases__)').ok, false);
  assert.equal(filtrarCodigo('print(__builtins__)').ok, false);
});
