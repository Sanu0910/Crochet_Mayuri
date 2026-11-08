// Checks the app reads the website's product list the same way the site
// does: every card in index.html becomes one product, nothing is lost.

import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:mayuriz/catalogue.dart';

void main() {
  final html = File('../index.html').readAsStringSync();

  test('reads every product from the live index.html', () {
    final cat = parseSite(html, live: true);
    final expected = RegExp(r"^\s*image: 'images/", multiLine: true).allMatches(html).length;
    expect(cat.products.length, expected);
    expect(cat.products.length, greaterThan(10));

    final ids = cat.products.map((p) => p.id).toSet();
    expect(ids.length, cat.products.length, reason: 'ids are unique');
    for (final p in cat.products) {
      expect(p.sku, startsWith('MZ-'), reason: p.id);
      expect(p.name, isNotEmpty, reason: p.id);
      expect(p.desc, isNotEmpty, reason: p.id);
      expect(p.image, startsWith('images/'), reason: p.id);
    }
  });

  test('reads categories, and every product belongs to one', () {
    final cat = parseSite(html, live: true);
    final keys = cat.categories.map((c) => c.key).toSet();
    expect(keys, containsAll(['all', 'fresh', 'scrunchies', 'bows']));
    for (final p in cat.products) {
      expect(keys, contains(p.cat), reason: p.id);
    }
    expect(cat.justIn.length, lessThanOrEqualTo(10));
  });

  test('handles quotes and escapes in text', () {
    final m = JsLiteral(r"{ name: 'Mayuri\'s Rose', fresh: true, n: 3 /* c */ }").objects().first;
    expect(m['name'], "Mayuri's Rose");
    expect(m['fresh'], true);
    expect(m['n'], 3);
  });

  test('order link pre-fills the website form', () {
    final p = parseSite(html, live: true).products.first;
    expect(p.orderUrl, '$siteUrl/?order=${p.id}#order');
  });
}
