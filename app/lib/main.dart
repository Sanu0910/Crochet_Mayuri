// Mayuri's Yarn Tales: the shop app. Shows the same products as the
// website (see catalogue.dart); orders go through the website's order form
// or by email, so nothing new to manage.

import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

import 'catalogue.dart';

const ink = Color(0xFF1D1D1F);
const inkSoft = Color(0xFF6E6E73);
const accent = Color(0xFFC8564A); // thread red
const rose = Color(0xFFE58FA3); // yarn rose
const cream = Color(0xFFFBF3EE);
const surfaceAlt = Color(0xFFF6F4F1);

void main() => runApp(const MayurizApp());

class MayurizApp extends StatelessWidget {
  const MayurizApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: "Mayuri's Yarn Tales",
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: accent,
          primary: accent,
          surface: Colors.white,
        ),
        scaffoldBackgroundColor: Colors.white,
      ),
      home: const HomePage(),
    );
  }
}

TextStyle script(double size, {Color color = ink, FontWeight w = FontWeight.w700}) =>
    TextStyle(fontFamily: 'Caveat', fontSize: size, color: color, fontWeight: w, height: 1.1);

Future<void> openLink(BuildContext context, String url) async {
  final ok = await launchUrl(Uri.parse(url), mode: LaunchMode.externalApplication);
  if (!ok && context.mounted) {
    ScaffoldMessenger.of(context)
        .showSnackBar(SnackBar(content: Text('Could not open $url')));
  }
}

String emailLink(Product? p) {
  final subject = p == null ? "Custom order (Mayuri's Yarn Tales app)" : 'Order: ${p.name} (${p.sku})';
  final body = p == null
      ? "Hi Mayuri! I'd love a custom piece. Here's what I have in mind:\n\n"
      : "Hi Mayuri! I'd love to order the \"${p.name}\" (code ${p.sku}). "
          'Could you share colour options, sizing and price?\n\n';
  return Uri(scheme: 'mailto', path: shopEmail, query: _q({'subject': subject, 'body': body})).toString();
}

// mailto needs %20 for spaces, not '+'
String _q(Map<String, String> m) =>
    m.entries.map((e) => '${e.key}=${Uri.encodeComponent(e.value)}').join('&');

// ---------------------------------------------------------------- home

class HomePage extends StatefulWidget {
  const HomePage({super.key});
  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  Catalogue? _cat;
  String _filter = 'all';
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final c = await loadCatalogue();
    if (!mounted) return;
    setState(() {
      _cat = c;
      _loading = false;
      if (!c.usedCategories.any((x) => x.key == _filter)) _filter = 'all';
    });
    if (!c.live) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
          content: Text("You're offline: showing the last saved collection.")));
    }
  }

  @override
  Widget build(BuildContext context) {
    final cat = _cat;
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.white,
        surfaceTintColor: Colors.white,
        titleSpacing: 16,
        title: Row(children: [
          Image.asset('assets/logo_mark.png', width: 30, height: 30),
          const SizedBox(width: 10),
          Text("Mayuri's Yarn Tales", style: script(26)),
        ]),
        bottom: const PreferredSize(
            preferredSize: Size.fromHeight(1),
            child: Divider(height: 1, color: Color(0x1A000000))),
      ),
      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: accent,
        foregroundColor: Colors.white,
        onPressed: () => openLink(context, '$siteUrl/#order'),
        icon: const Icon(Icons.edit_note),
        label: const Text('Custom order'),
      ),
      body: _loading || cat == null
          ? const Center(child: CircularProgressIndicator(color: accent))
          : RefreshIndicator(
              color: accent,
              onRefresh: _load,
              child: CustomScrollView(slivers: [
                SliverToBoxAdapter(child: _hero()),
                if (cat.justIn.isNotEmpty) ...[
                  _heading('Just in', 'New this week.'),
                  SliverToBoxAdapter(child: _justIn(cat.justIn)),
                ],
                _heading('The collection', 'Every piece, made by hand.'),
                SliverToBoxAdapter(child: _chips(cat)),
                _grid(cat.inCategory(_filter)),
                SliverToBoxAdapter(child: _footer()),
              ]),
            ),
    );
  }

  Widget _hero() => Padding(
        padding: const EdgeInsets.fromLTRB(24, 28, 24, 8),
        child: Column(children: [
          Image.asset('assets/logo_mark.png', width: 96, height: 96),
          const SizedBox(height: 10),
          Text("Mayuri's Yarn Tales", style: script(38), textAlign: TextAlign.center),
          const SizedBox(height: 4),
          Text('handmade crochet · made to order in India',
              style: script(20, color: accent, w: FontWeight.w600), textAlign: TextAlign.center),
          const SizedBox(height: 18),
          const Text(
            'Crochet scrunchies, hair clips, bows, roses and keychains, each one '
            'hooked by hand, in any colour you like.',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 16, color: inkSoft, height: 1.4),
          ),
        ]),
      );

  Widget _heading(String eyebrow, String title) => SliverToBoxAdapter(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(16, 28, 16, 12),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(eyebrow,
                style: const TextStyle(color: accent, fontWeight: FontWeight.w600, fontSize: 14)),
            const SizedBox(height: 2),
            Text(title,
                style: const TextStyle(color: ink, fontWeight: FontWeight.w700, fontSize: 24)),
          ]),
        ),
      );

  Widget _justIn(List<Product> items) => SizedBox(
        height: 230,
        child: ListView.separated(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          scrollDirection: Axis.horizontal,
          itemCount: items.length,
          separatorBuilder: (_, _) => const SizedBox(width: 12),
          itemBuilder: (_, i) => SizedBox(width: 160, child: ProductCard(items[i])),
        ),
      );

  Widget _chips(Catalogue cat) => SizedBox(
        height: 44,
        child: ListView(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          scrollDirection: Axis.horizontal,
          children: [
            for (final c in cat.usedCategories)
              Padding(
                padding: const EdgeInsets.only(right: 8),
                child: ChoiceChip(
                  label: Text(c.label),
                  selected: _filter == c.key,
                  showCheckmark: false,
                  selectedColor: ink,
                  labelStyle: TextStyle(color: _filter == c.key ? Colors.white : ink),
                  onSelected: (_) => setState(() => _filter = c.key),
                ),
              ),
          ],
        ),
      );

  Widget _grid(List<Product> items) => SliverPadding(
        padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
        sliver: SliverGrid(
          gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
            maxCrossAxisExtent: 220,
            mainAxisSpacing: 14,
            crossAxisSpacing: 12,
            childAspectRatio: 0.72,
          ),
          delegate: SliverChildBuilderDelegate(
            (_, i) => ProductCard(items[i]),
            childCount: items.length,
          ),
        ),
      );

  Widget _footer() => Container(
        margin: const EdgeInsets.only(top: 28),
        padding: const EdgeInsets.fromLTRB(24, 28, 24, 100),
        color: surfaceAlt,
        child: Column(children: [
          Text("Something you don't see here?", style: script(26)),
          const SizedBox(height: 8),
          const Text(
            'Mayuri makes pieces to order in any colour. Tell her what you have in mind.',
            textAlign: TextAlign.center,
            style: TextStyle(color: inkSoft, fontSize: 15, height: 1.4),
          ),
          const SizedBox(height: 14),
          Wrap(spacing: 10, runSpacing: 10, alignment: WrapAlignment.center, children: [
            OutlinedButton.icon(
              onPressed: () => openLink(context, emailLink(null)),
              icon: const Icon(Icons.mail_outline),
              label: const Text('Email Mayuri'),
            ),
            OutlinedButton.icon(
              onPressed: () => openLink(context, siteUrl),
              icon: const Icon(Icons.public),
              label: const Text('Open website'),
            ),
          ]),
        ]),
      );
}

// ---------------------------------------------------------------- card

class ProductCard extends StatelessWidget {
  final Product p;
  const ProductCard(this.p, {super.key});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => Navigator.of(context)
          .push(MaterialPageRoute(builder: (_) => ProductPage(p))),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Expanded(
          child: Stack(children: [
            Positioned.fill(
              child: Hero(
                tag: 'img-${p.id}',
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(16),
                  child: ProductImage(p),
                ),
              ),
            ),
            if (p.badge.isNotEmpty)
              Positioned(
                left: 8,
                top: 8,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                      color: Colors.white.withValues(alpha: 0.92),
                      borderRadius: BorderRadius.circular(20)),
                  child: Text(p.badge,
                      style: const TextStyle(
                          fontSize: 11, fontWeight: FontWeight.w600, color: accent)),
                ),
              ),
          ]),
        ),
        const SizedBox(height: 8),
        Text(p.tag, style: const TextStyle(fontSize: 12, color: inkSoft)),
        Text(p.name,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: ink)),
      ]),
    );
  }
}

class ProductImage extends StatelessWidget {
  final Product p;
  const ProductImage(this.p, {super.key});

  @override
  Widget build(BuildContext context) {
    return Image.network(
      p.imageUrl,
      fit: BoxFit.cover,
      width: double.infinity,
      loadingBuilder: (_, child, progress) =>
          progress == null ? child : Container(color: cream),
      errorBuilder: (_, _, _) => Container(
        color: cream,
        alignment: Alignment.center,
        child: Image.asset('assets/logo_mark.png', width: 48, opacity: const AlwaysStoppedAnimation(0.5)),
      ),
    );
  }
}

// ---------------------------------------------------------------- product

class ProductPage extends StatelessWidget {
  final Product p;
  const ProductPage(this.p, {super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.white,
        surfaceTintColor: Colors.white,
        title: Text(p.tag, style: const TextStyle(fontSize: 17)),
      ),
      body: ListView(children: [
        AspectRatio(
          aspectRatio: 1,
          child: Hero(tag: 'img-${p.id}', child: ProductImage(p)),
        ),
        Padding(
          padding: const EdgeInsets.fromLTRB(20, 20, 20, 32),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Row(children: [
              if (p.badge.isNotEmpty) ...[
                Text(p.badge,
                    style: const TextStyle(color: accent, fontWeight: FontWeight.w600)),
                const Text('  ·  ', style: TextStyle(color: inkSoft)),
              ],
              Text(p.sku, style: const TextStyle(color: inkSoft, fontFamily: 'monospace')),
            ]),
            const SizedBox(height: 6),
            Text(p.name,
                style: const TextStyle(fontSize: 26, fontWeight: FontWeight.w700, color: ink)),
            const SizedBox(height: 12),
            Text(p.desc, style: const TextStyle(fontSize: 16, color: inkSoft, height: 1.5)),
            const SizedBox(height: 10),
            Text('Made to order, in any colour you like.',
                style: script(20, color: accent, w: FontWeight.w600)),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              child: FilledButton.icon(
                style: FilledButton.styleFrom(
                    backgroundColor: accent,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: const StadiumBorder()),
                onPressed: () => openLink(context, p.orderUrl),
                icon: const Icon(Icons.shopping_bag_outlined),
                label: const Text('Order this', style: TextStyle(fontSize: 17)),
              ),
            ),
            const SizedBox(height: 10),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    shape: const StadiumBorder()),
                onPressed: () => openLink(context, emailLink(p)),
                icon: const Icon(Icons.mail_outline),
                label: const Text('Ask by email'),
              ),
            ),
            const SizedBox(height: 12),
            const Text(
              '"Order this" opens the order form on the website with this piece '
              'already filled in. Mayuri replies personally with colours and price.',
              style: TextStyle(fontSize: 13, color: inkSoft, height: 1.4),
            ),
          ]),
        ),
      ]),
    );
  }
}
