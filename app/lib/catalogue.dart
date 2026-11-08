// Reads the shop's products straight from the live website, so the app
// always matches it: the Telegram bot adds a product to index.html and the
// app shows it on the next refresh. No separate database to keep in step.
//
// The products live in index.html between /* PRODUCTS:START */ and
// /* PRODUCTS:END */ as a JavaScript list; categories in `const CATEGORIES`.
// The last good copy is saved on the phone; a copy bundled with the app is
// the fallback for the very first start without internet.

import 'package:flutter/services.dart' show rootBundle;
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

const siteUrl = 'https://mayurisyarntales.online';
const shopEmail = 'mayurighoshblg@gmail.com';

class Product {
  final String id, sku, name, cat, tag, badge, desc, image;
  final bool fresh;
  Product(Map<String, Object?> m)
      : id = '${m['id'] ?? ''}',
        sku = '${m['sku'] ?? ''}',
        name = '${m['name'] ?? ''}',
        cat = '${m['cat'] ?? ''}',
        tag = '${m['tag'] ?? ''}',
        badge = '${m['badge'] ?? ''}',
        desc = '${m['desc'] ?? ''}',
        image = '${m['image'] ?? ''}',
        fresh = m['fresh'] == true;

  String get imageUrl => '$siteUrl/$image';
  String get orderUrl => '$siteUrl/?order=${Uri.encodeComponent(id)}#order';
}

class Category {
  final String key, label;
  Category(this.key, this.label);
}

class Catalogue {
  final List<Product> products;
  final List<Category> categories;
  final bool live; // false when shown from a saved / bundled copy
  Catalogue(this.products, this.categories, this.live);

  List<Product> get justIn => products.where((p) => p.fresh).take(10).toList();

  List<Product> inCategory(String key) {
    if (key == 'all') return products;
    if (key == 'fresh') return products.where((p) => p.fresh).toList();
    return products.where((p) => p.cat == key).toList();
  }

  /// Only categories that have at least one product.
  List<Category> get usedCategories => categories
      .where((c) => c.key == 'all' || inCategory(c.key).isNotEmpty)
      .toList();
}

const _cacheKey = 'site_html_v1';

Future<Catalogue> loadCatalogue() async {
  final prefs = await SharedPreferences.getInstance();
  try {
    final res = await http
        .get(Uri.parse('$siteUrl/index.html'))
        .timeout(const Duration(seconds: 15));
    if (res.statusCode == 200) {
      final cat = parseSite(res.body, live: true);
      if (cat.products.isNotEmpty) {
        await prefs.setString(_cacheKey, res.body);
        return cat;
      }
    }
  } catch (_) {
    // offline or slow: fall through to the saved copy
  }
  final saved = prefs.getString(_cacheKey);
  if (saved != null) return parseSite(saved, live: false);
  return parseSite(await rootBundle.loadString('assets/site_snapshot.html'),
      live: false);
}

Catalogue parseSite(String html, {required bool live}) {
  final products = <Product>[];
  final a = html.indexOf('/* PRODUCTS:START */');
  final b = html.indexOf('/* PRODUCTS:END */');
  if (a >= 0 && b > a) {
    for (final m in JsLiteral(html.substring(a + 20, b)).objects()) {
      final p = Product(m);
      if (p.id.isNotEmpty && p.image.isNotEmpty) products.add(p);
    }
  }
  final categories = <Category>[];
  final c = html.indexOf('const CATEGORIES');
  if (c >= 0) {
    final start = html.indexOf('[', c), end = html.indexOf('];', c);
    if (start > 0 && end > start) {
      for (final m in JsLiteral(html.substring(start + 1, end)).objects()) {
        categories.add(Category('${m['key']}', '${m['label']}'));
      }
    }
  }
  if (categories.isEmpty) categories.add(Category('all', 'All'));
  return Catalogue(products, categories, live);
}

/// A tiny reader for the simple object literals the site uses:
/// `{ key: 'text', flag: true, n: 3 }`, separated by commas, with comments.
class JsLiteral {
  final String s;
  int i = 0;
  JsLiteral(this.s);

  Iterable<Map<String, Object?>> objects() sync* {
    while (true) {
      _skip();
      if (i >= s.length) return;
      if (s[i] == '{') {
        i++;
        yield _object();
      } else {
        i++; // stray character (comma etc.)
      }
    }
  }

  void _skip() {
    while (i < s.length) {
      final ch = s[i];
      if (ch == ' ' || ch == '\n' || ch == '\r' || ch == '\t' || ch == ',') {
        i++;
      } else if (s.startsWith('//', i)) {
        final e = s.indexOf('\n', i);
        i = e < 0 ? s.length : e + 1;
      } else if (s.startsWith('/*', i)) {
        final e = s.indexOf('*/', i + 2);
        i = e < 0 ? s.length : e + 2;
      } else {
        return;
      }
    }
  }

  Map<String, Object?> _object() {
    final m = <String, Object?>{};
    while (true) {
      _skip();
      if (i >= s.length) return m;
      if (s[i] == '}') {
        i++;
        return m;
      }
      final key = (s[i] == "'" || s[i] == '"') ? _string() : _word();
      _skip();
      if (i < s.length && s[i] == ':') i++;
      _skip();
      m[key] = _value();
    }
  }

  Object? _value() {
    if (i >= s.length) return null;
    final ch = s[i];
    if (ch == "'" || ch == '"' || ch == '`') return _string();
    if (ch == '{') {
      i++;
      return _object();
    }
    final w = _word();
    if (w == 'true') return true;
    if (w == 'false') return false;
    if (w == 'null') return null;
    return num.tryParse(w) ?? w;
  }

  String _word() {
    final st = i;
    while (i < s.length && RegExp(r'[A-Za-z0-9_$.\-]').hasMatch(s[i])) {
      i++;
    }
    if (i == st) i++; // never stall on an unexpected character
    return s.substring(st, i);
  }

  String _string() {
    final q = s[i++];
    final b = StringBuffer();
    while (i < s.length && s[i] != q) {
      if (s[i] == '\\' && i + 1 < s.length) {
        final n = s[i + 1];
        b.write(n == 'n' ? '\n' : n == 't' ? '\t' : n);
        i += 2;
      } else {
        b.write(s[i++]);
      }
    }
    i++; // closing quote
    return b.toString();
  }
}
